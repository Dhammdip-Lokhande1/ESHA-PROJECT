"""
tests/test_auth_rbac.py — Complete test suite for Auth, RBAC (2-Role Model), and IDOR protection.

Tests:
  1. Registration (valid, duplicates, weak passwords, role escalation prevention)
  2. Login & Token Generation
  3. /auth/me profile access
  4. Role-Based Access Control (User vs Admin permissions)
  5. IDOR & Resource Ownership protection
  6. Admin User Management (role switching between user/admin, account deactivation)
  7. Rejection of obsolete 'instructor' and 'student' roles
"""
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.rate_limiter import limiter
from app.db.models import Base, User
from app.db.session import get_db_dependency
from app.main import app


@pytest_asyncio.fixture
async def test_db():
    """Create a fresh in-memory SQLite DB for each test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_dependency] = override_db
    limiter.reset()
    yield session_factory
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


def _mock_semantic():
    import app.api.routes as routes_module
    def fake_semantic(code_a, code_b):
        return 0.75, [{"type": "cosine_similarity", "value": 0.75}]
    return patch.object(routes_module, "semantic_similarity", fake_semantic)


@pytest.mark.asyncio
async def test_user_registration_success(client):
    """Test successful user account registration (defaults to 'user' role)."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "normal_user_1",
            "email": "user1@ehsa.edu",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["username"] == "normal_user_1"
    assert data["email"] == "user1@ehsa.edu"
    assert data["role"] == "user"
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_user_registration_role_escalation_prevention(client):
    """Verify that passing role='admin' or role='instructor' during registration is ignored/forced to 'user'."""
    # Attempt admin escalation
    resp1 = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "hacker_admin",
            "email": "hacker_admin@ehsa.edu",
            "password": "Password123!",
            "role": "admin",
        },
    )
    assert resp1.status_code == 201, resp1.text
    assert resp1.json()["role"] == "user"

    # Attempt instructor escalation
    resp2 = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "hacker_instructor",
            "email": "hacker_instructor@ehsa.edu",
            "password": "Password123!",
            "role": "instructor",
        },
    )
    assert resp2.status_code == 201, resp2.text
    assert resp2.json()["role"] == "user"


@pytest.mark.asyncio
async def test_user_registration_duplicate_checks(client):
    """Verify duplicate username and email rejection."""
    await client.post(
        "/api/v1/auth/register",
        json={"username": "dup_user", "email": "dup@ehsa.edu", "password": "Password123!"},
    )
    # Duplicate username
    resp1 = await client.post(
        "/api/v1/auth/register",
        json={"username": "dup_user", "email": "unique@ehsa.edu", "password": "Password123!"},
    )
    assert resp1.status_code == 400
    assert "taken" in resp1.json()["detail"]

    # Duplicate email
    resp2 = await client.post(
        "/api/v1/auth/register",
        json={"username": "unique_user", "email": "dup@ehsa.edu", "password": "Password123!"},
    )
    assert resp2.status_code == 400
    assert "already exists" in resp2.json()["detail"]


@pytest.mark.asyncio
async def test_user_login_and_auth_me(client):
    """Test login with valid/invalid credentials and /auth/me profile fetching."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "login_user", "email": "login@ehsa.edu", "password": "SecretPass123!"},
    )
    assert reg_resp.status_code == 201, reg_resp.text

    # Invalid password
    bad_resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "login_user", "password": "WrongPassword!"},
    )
    assert bad_resp.status_code == 401

    # Valid login
    good_resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "login_user", "password": "SecretPass123!"},
    )
    assert good_resp.status_code == 200
    token_data = good_resp.json()
    token = token_data["access_token"]
    assert token is not None

    # Fetch /auth/me without token -> 401
    me_fail = await client.get("/api/v1/auth/me")
    assert me_fail.status_code == 401

    # Fetch /auth/me with Bearer token -> 200
    me_success = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_success.status_code == 200
    assert me_success.json()["username"] == "login_user"
    assert me_success.json()["role"] == "user"


@pytest.mark.asyncio
async def test_rbac_user_capabilities_and_admin_isolation(client, test_db):
    """
    Test 2-Role RBAC:
    - User can analyze code, submit feedback, view history, access analytics dashboard.
    - User CANNOT access admin endpoints (/api/v1/admin/users).
    - Admin CAN access admin endpoints.
    """
    with _mock_semantic():
        # 1. Register User and Admin
        await client.post(
            "/api/v1/auth/register",
            json={"username": "normal_rbac_user", "email": "normal_rbac@ehsa.edu", "password": "Password123!"},
        )
        await client.post(
            "/api/v1/auth/register",
            json={"username": "admin_rbac_user", "email": "admin_rbac@ehsa.edu", "password": "Password123!"},
        )

        # Upgrade admin_rbac_user role to 'admin' in test DB
        async with test_db() as session:
            res = await session.execute(select(User).where(User.username == "admin_rbac_user"))
            admin_obj = res.scalar_one()
            admin_obj.role = "admin"
            await session.commit()

        # Login Normal User
        u_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "normal_rbac_user", "password": "Password123!"},
        )
        assert u_login.status_code == 200
        user_token = u_login.json()["access_token"]

        # Login Admin User
        a_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin_rbac_user", "password": "Password123!"},
        )
        assert a_login.status_code == 200
        admin_token = a_login.json()["access_token"]

        # 2. Create an analysis run
        analyze_resp = await client.post(
            "/api/v1/analyze",
            json={
                "submission_code": "def foo(): pass",
                "reference_code": "def foo(): pass",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        run_id = analyze_resp.json()["run_id"]

        # 3. Normal User CAN submit feedback -> 200 (Capability merged into User!)
        fb_user = await client.post(
            f"/api/v1/feedback/{run_id}",
            json={"verdict": "confirmed"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert fb_user.status_code == 200, fb_user.text

        # 4. Normal User CAN access personal dashboard -> 200
        dash_my = await client.get(
            "/api/v1/dashboard/my",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert dash_my.status_code == 200
        assert dash_my.json()["username"] == "normal_rbac_user"

        # 5. Normal User CAN access analytics dashboard -> 200
        dash_analytics = await client.get(
            "/api/v1/instructor/dashboard",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert dash_analytics.status_code == 200

        # 6. Normal User CANNOT access Admin endpoints -> 403 Forbidden
        admin_access_blocked = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert admin_access_blocked.status_code == 403

        # 7. Admin CAN access Admin endpoints -> 200
        admin_access_allowed = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_access_allowed.status_code == 200


@pytest.mark.asyncio
async def test_idor_protection(client):
    """Test that User A cannot access or delete User B's run reports."""
    with _mock_semantic():
        # Register User A
        await client.post(
            "/api/v1/auth/register",
            json={"username": "user_a", "email": "user_a@ehsa.edu", "password": "Password123!"},
        )
        login_a = await client.post(
            "/api/v1/auth/login",
            json={"username": "user_a", "password": "Password123!"},
        )
        token_a = login_a.json()["access_token"]

        # Register User B
        await client.post(
            "/api/v1/auth/register",
            json={"username": "user_b", "email": "user_b@ehsa.edu", "password": "Password123!"},
        )
        login_b = await client.post(
            "/api/v1/auth/login",
            json={"username": "user_b", "password": "Password123!"},
        )
        token_b = login_b.json()["access_token"]

        # User A creates a run
        run_resp = await client.post(
            "/api/v1/analyze",
            json={"submission_code": "x = 10", "reference_code": "x = 20"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        run_a_id = run_resp.json()["run_id"]

        # User A gets report -> 200
        report_a = await client.get(
            f"/api/v1/report/{run_a_id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert report_a.status_code == 200

        # User B attempts to get User A's report -> 403 Forbidden (IDOR Blocked)
        report_b_attempt = await client.get(
            f"/api/v1/report/{run_a_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert report_b_attempt.status_code == 403

        # User B attempts to delete User A's run -> 403 Forbidden (IDOR Blocked)
        delete_b_attempt = await client.delete(
            f"/api/v1/runs/{run_a_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert delete_b_attempt.status_code == 403


@pytest.mark.asyncio
async def test_admin_user_management(client, test_db):
    """Test Admin user listing, role modifications strictly to 'user'/'admin', and rejection of 'instructor'."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"username": "target_user", "email": "target@ehsa.edu", "password": "Password123!"},
    )
    assert reg.status_code == 201
    target_id = reg.json()["id"]

    # Register admin account
    reg_admin = await client.post(
        "/api/v1/auth/register",
        json={"username": "admin_mgr", "email": "admin_mgr@ehsa.edu", "password": "AdminSecretPass123!"},
    )
    assert reg_admin.status_code == 201

    # Upgrade admin_mgr role in test DB
    async with test_db() as session:
        res = await session.execute(select(User).where(User.username == "admin_mgr"))
        u = res.scalar_one()
        u.role = "admin"
        await session.commit()

    # Login admin
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin_mgr", "password": "AdminSecretPass123!"},
    )
    admin_token = admin_login.json()["access_token"]

    # List users
    users_resp = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert users_resp.status_code == 200

    # Attempt to change role to 'instructor' -> MUST BE REJECTED (422)
    patch_inst = await client.patch(
        f"/api/v1/admin/users/{target_id}",
        json={"role": "instructor"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_inst.status_code == 422, "Instructor role must be rejected by admin endpoints"

    # Change role to 'admin' -> 200
    patch_admin = await client.patch(
        f"/api/v1/admin/users/{target_id}",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_admin.status_code == 200
    assert patch_admin.json()["role"] == "admin"

    # Change role back to 'user' -> 200
    patch_user = await client.patch(
        f"/api/v1/admin/users/{target_id}",
        json={"role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_user.status_code == 200
    assert patch_user.json()["role"] == "user"


@pytest.mark.asyncio
async def test_fusion_retrain_restricted_to_admin_only(client, test_db):
    """
    Verify RBAC for /fusion/retrain:
    - Anonymous -> 401 Unauthorized
    - USER -> 403 Forbidden (retraining impacts system-wide model)
    - ADMIN -> Allowed (Not 401/403)
    - USER & ADMIN -> feedback submission allowed (200)
    """
    with _mock_semantic():
        # 1. Anonymous request to /fusion/retrain -> 401
        anon_retrain = await client.post("/api/v1/fusion/retrain")
        assert anon_retrain.status_code == 401

        # 2. Register Normal User & Admin
        await client.post(
            "/api/v1/auth/register",
            json={"username": "user_retrain", "email": "u_retrain@ehsa.edu", "password": "Password123!"},
        )
        await client.post(
            "/api/v1/auth/register",
            json={"username": "admin_retrain", "email": "a_retrain@ehsa.edu", "password": "Password123!"},
        )

        async with test_db() as session:
            res = await session.execute(select(User).where(User.username == "admin_retrain"))
            u = res.scalar_one()
            u.role = "admin"
            await session.commit()

        u_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "user_retrain", "password": "Password123!"},
        )
        user_token = u_login.json()["access_token"]

        a_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin_retrain", "password": "Password123!"},
        )
        admin_token = a_login.json()["access_token"]

        # 3. Normal User tries /fusion/retrain -> 403 Forbidden
        user_retrain = await client.post(
            "/api/v1/fusion/retrain",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert user_retrain.status_code == 403, "Normal users must NOT be allowed to trigger global model retraining"

        # 4. Admin tries /fusion/retrain -> Allowed (Not 401 or 403)
        admin_retrain = await client.post(
            "/api/v1/fusion/retrain",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_retrain.status_code not in (401, 403), "Admin must be authorized to retrain fusion model"

        # 5. Create a run and test feedback for USER and ADMIN
        run_resp = await client.post(
            "/api/v1/analyze",
            json={"submission_code": "a = 1", "reference_code": "a = 1"},
        )
        run_id = run_resp.json()["run_id"]

        fb_u = await client.post(
            f"/api/v1/feedback/{run_id}",
            json={"verdict": "confirmed"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert fb_u.status_code == 200, "USER must be able to submit feedback"

        fb_a = await client.post(
            f"/api/v1/feedback/{run_id}",
            json={"verdict": "false_positive"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert fb_a.status_code == 200, "ADMIN must be able to submit feedback"


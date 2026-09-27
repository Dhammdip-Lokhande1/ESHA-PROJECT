"""
experiments/generate_inventory.py
==================================
Generates docs/inventory.json summarizing system endpoints, DB tables/schemas,
and test suite breakdown for thesis reporting.
"""
import json
import os
import sys
import sqlite3
import pytest

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app
from app.config import settings

def generate_inventory():
    print("[+] Collecting API routes...")
    routes_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes_info.append({
                "path": route.path,
                "name": getattr(route, "name", ""),
                "methods": list(route.methods) if route.methods else []
            })
    
    print(f"    Total API endpoints found: {len(routes_info)}")

    print("[+] Inspecting SQLite database schema...")
    db_schema = {}
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", db_path))

    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]
        
        for table in sorted(tables):
            cursor.execute(f"PRAGMA table_info({table});")
            cols = [{"cid": row[0], "name": row[1], "type": row[2], "notnull": bool(row[3]), "dflt_value": row[4], "pk": bool(row[5])} for row in cursor.fetchall()]
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cursor.fetchone()[0]
            db_schema[table] = {
                "columns": cols,
                "row_count": row_count
            }
        conn.close()
    else:
        print(f"    WARNING: DB_PATH {db_path} not found.")


    print("[+] Reading test suite structure...")
    test_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "tests")
    test_files = [f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")]
    
    inventory = {
        "generated_at": "2026-09-20",
        "api_routes": {
            "count": len(routes_info),
            "endpoints": routes_info
        },
        "database": {
            "db_path": str(db_path),
            "table_count": len(db_schema),
            "tables": db_schema
        },

        "test_suite": {
            "test_files_count": len(test_files),
            "test_files": sorted(test_files)
        }
    }

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "inventory.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
    
    print(f"[OK] Inventory successfully generated at {out_path}")


if __name__ == "__main__":
    generate_inventory()

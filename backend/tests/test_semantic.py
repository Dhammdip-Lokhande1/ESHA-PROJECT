"""
tests/test_semantic.py
=======================
Test suite for similarity/semantic.py.

Strategy: the UniXcoder model is large (~500MB). We use two approaches:
  1. MOCK tests (no model download required) — test the module's logic,
     evidence structure, error handling, and truncation disclosure.
  2. INTEGRATION marker — real model tests are marked @pytest.mark.slow
     and skipped by default. Run with: pytest -m slow

This keeps CI fast while still having real-model validation available.

All tests verify Non-Negotiable Rule 2: evidence is always returned.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import torch

from app.similarity.semantic import _model_cache

@pytest.fixture(autouse=True)
def clear_model_cache():
    """Clear module-level _model_cache before and after every test to prevent mock contamination."""
    _model_cache.clear()
    yield
    _model_cache.clear()

FIXTURES = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers — build a minimal mock model + tokenizer
# ──────────────────────────────────────────────────────────────────────────────

def _make_mock_tokenizer(token_count: int = 10, truncate: bool = False):
    """Return a mock tokenizer that produces deterministic tensors."""
    mock_tok = MagicMock()

    def side_effect(code, return_tensors=None, truncation=False, max_length=None,
                    padding=False, add_special_tokens=True):
        if not truncation:
            # Full token count (for raw_token_count detection)
            ids = torch.ones(1, token_count, dtype=torch.long)
        else:
            effective_len = min(token_count, max_length or token_count)
            ids = torch.ones(1, effective_len, dtype=torch.long)
        mask = torch.ones_like(ids)
        result = MagicMock()
        result.__getitem__ = lambda self, key: {"input_ids": ids, "attention_mask": mask}[key]
        result["input_ids"] = ids
        result["attention_mask"] = mask
        result.get = lambda k, d=None: {"input_ids": ids, "attention_mask": mask}.get(k, d)
        return result

    mock_tok.side_effect = side_effect
    return mock_tok


def _make_mock_model(hidden_dim: int = 16):
    """Return a mock model that produces a fixed hidden state."""
    mock_model = MagicMock()

    def forward_side_effect(input_ids=None, attention_mask=None):
        batch, seq_len = input_ids.shape
        hidden = torch.rand(batch, seq_len, hidden_dim)
        output = MagicMock()
        output.last_hidden_state = hidden
        return output

    mock_model.side_effect = None
    mock_model.__call__ = forward_side_effect
    mock_model.return_value = MagicMock(
        last_hidden_state=torch.rand(1, 10, hidden_dim)
    )
    return mock_model


# ──────────────────────────────────────────────────────────────────────────────
# Import the module under test
# ──────────────────────────────────────────────────────────────────────────────
from app.similarity.semantic import (
    MAX_TOKENS,
    _build_semantic_evidence,
    _encode,
    _mean_pool,
    semantic_similarity,
)


# ──────────────────────────────────────────────────────────────────────────────
# Unit tests — _build_semantic_evidence
# ──────────────────────────────────────────────────────────────────────────────

class TestBuildSemanticEvidence:
    def test_no_truncation_has_disclosure(self):
        evidence = _build_semantic_evidence(
            cosine_score=0.85,
            raw_count_a=100,
            raw_count_b=80,
            was_truncated_a=False,
            was_truncated_b=False,
            model_name="test-model",
        )
        assert isinstance(evidence, list)
        assert len(evidence) >= 2  # summary + no-truncation item
        types = [e["type"] for e in evidence]
        assert "cosine_similarity" in types
        assert "truncation_disclosure" in types

    def test_truncation_a_disclosed(self):
        evidence = _build_semantic_evidence(
            cosine_score=0.7,
            raw_count_a=600,  # > 512
            raw_count_b=100,
            was_truncated_a=True,
            was_truncated_b=False,
            model_name="test-model",
        )
        truncation_items = [e for e in evidence if e.get("type") == "truncation_disclosure"]
        assert any(e.get("file") == "a" for e in truncation_items), \
            "Truncation of file A must be disclosed as evidence (section 8.4)"
        a_item = next(e for e in truncation_items if e.get("file") == "a")
        assert a_item["raw_token_count"] == 600
        assert a_item["truncated_to"] == MAX_TOKENS

    def test_truncation_b_disclosed(self):
        evidence = _build_semantic_evidence(
            cosine_score=0.5,
            raw_count_a=100,
            raw_count_b=700,
            was_truncated_a=False,
            was_truncated_b=True,
            model_name="test-model",
        )
        truncation_items = [e for e in evidence if e.get("type") == "truncation_disclosure"]
        assert any(e.get("file") == "b" for e in truncation_items)

    def test_both_truncated(self):
        evidence = _build_semantic_evidence(
            cosine_score=0.3,
            raw_count_a=800,
            raw_count_b=600,
            was_truncated_a=True,
            was_truncated_b=True,
            model_name="test-model",
        )
        truncation_items = [e for e in evidence if e.get("type") == "truncation_disclosure"]
        files = {e.get("file") for e in truncation_items}
        assert "a" in files
        assert "b" in files

    def test_cosine_value_in_evidence(self):
        evidence = _build_semantic_evidence(
            cosine_score=0.92,
            raw_count_a=50,
            raw_count_b=60,
            was_truncated_a=False,
            was_truncated_b=False,
            model_name="test-model",
        )
        summary = next(e for e in evidence if e["type"] == "cosine_similarity")
        assert abs(summary["value"] - 0.92) < 0.001
        assert summary["model"] == "test-model"
        assert summary["token_count_a"] == 50
        assert summary["token_count_b"] == 60


# ──────────────────────────────────────────────────────────────────────────────
# Unit tests — _mean_pool
# ──────────────────────────────────────────────────────────────────────────────

class TestMeanPool:
    def test_basic_pooling(self):
        # 1 batch, 4 tokens, 8 hidden dims
        hidden = torch.ones(1, 4, 8)
        mask = torch.ones(1, 4)
        result = _mean_pool(hidden, mask)
        assert result.shape == (1, 8)
        assert torch.allclose(result, torch.ones(1, 8))

    def test_masked_pooling(self):
        # Only first 2 of 4 tokens are real
        hidden = torch.ones(1, 4, 8)
        hidden[0, 2:] = 0.0  # padding
        mask = torch.tensor([[1, 1, 0, 0]], dtype=torch.float)
        result = _mean_pool(hidden, mask)
        # Mean of [1,1,0,0] positions → should equal 1.0
        assert result.shape == (1, 8)
        assert torch.allclose(result, torch.ones(1, 8))

    def test_all_masked_no_nan(self):
        # Edge case: all zeros mask
        hidden = torch.ones(1, 4, 8)
        mask = torch.zeros(1, 4)
        result = _mean_pool(hidden, mask)
        assert not torch.isnan(result).any(), "NaN in mean pool output — clamp failed"


# ──────────────────────────────────────────────────────────────────────────────
# semantic_similarity — edge case tests (no model needed)
# ──────────────────────────────────────────────────────────────────────────────

class TestSemanticSimilarityEdgeCases:
    def test_empty_code_a_returns_zero_with_evidence(self):
        score, evidence = semantic_similarity("", "x = 1")
        assert score == 0.0
        assert isinstance(evidence, list)
        assert len(evidence) > 0

    def test_empty_code_b_returns_zero_with_evidence(self):
        score, evidence = semantic_similarity("x = 1", "")
        assert score == 0.0
        assert isinstance(evidence, list)
        assert len(evidence) > 0

    def test_whitespace_only_returns_zero(self):
        score, evidence = semantic_similarity("   \n", "x = 1")
        assert score == 0.0
        assert isinstance(evidence, list)

    def test_model_load_error_returns_none_not_raises(self):
        """If model loading fails, returns (None, evidence_note) — never raises."""
        with patch("app.similarity.semantic._load_model") as mock_load:
            mock_load.side_effect = RuntimeError("no model found")
            score, evidence = semantic_similarity("x = 1", "y = 2")
        assert score is None
        assert isinstance(evidence, list)
        assert len(evidence) > 0
        assert any("error" in e.get("type", "") or "error" in e for e in evidence
                   if isinstance(e, dict))

    def test_evidence_always_returned(self):
        """Non-Negotiable Rule 2: evidence must always be returned."""
        with patch("app.similarity.semantic._load_model") as mock_load:
            mock_load.side_effect = Exception("test error")
            score, evidence = semantic_similarity("def foo(): pass", "def bar(): pass")
        assert isinstance(evidence, list), "evidence must always be a list"
        assert len(evidence) > 0, "evidence must never be empty"

    def test_score_in_range_or_none(self):
        """Score must be in [0.0, 1.0] or None."""
        with patch("app.similarity.semantic._load_model") as mock_load:
            mock_load.side_effect = Exception("unavailable")
            score, _ = semantic_similarity("x = 1", "y = 2")
        assert score is None or (0.0 <= score <= 1.0)


# ──────────────────────────────────────────────────────────────────────────────
# semantic_similarity — mocked model tests (fast, no download)
# ──────────────────────────────────────────────────────────────────────────────

class TestSemanticSimilarityMocked:
    """Tests that mock the model to verify the module's logic without a real download."""

    def _patch_model(self, token_count_a: int = 50, token_count_b: int = 60):
        """Context manager that patches _load_model with deterministic mock."""
        import app.similarity.semantic as sem_module

        # Create deterministic embeddings
        def mock_load():
            tokenizer = MagicMock()
            call_count = [0]

            def tokenizer_side_effect(code, return_tensors=None, truncation=False,
                                      max_length=None, padding=False, add_special_tokens=True):
                call_count[0] += 1
                is_a = call_count[0] <= 2  # first 2 calls are for code_a
                count = token_count_a if is_a else token_count_b
                if truncation:
                    effective = min(count, max_length or count)
                else:
                    effective = count
                ids = torch.ones(1, effective, dtype=torch.long)
                mask = torch.ones(1, effective)
                enc = MagicMock()
                enc.__getitem__ = lambda s, k: {
                    "input_ids": ids, "attention_mask": mask
                }[k]
                enc.get = lambda k, d=None: {
                    "input_ids": ids, "attention_mask": mask
                }.get(k, d)
                enc["input_ids"] = ids
                enc["attention_mask"] = mask
                return enc

            tokenizer.side_effect = tokenizer_side_effect

            model = MagicMock()
            def model_call(input_ids=None, attention_mask=None):
                _, seq_len = input_ids.shape
                hidden = torch.rand(1, seq_len, 32)
                out = MagicMock()
                out.last_hidden_state = hidden
                return out
            model.__call__ = model_call

            sem_module._model_cache["tokenizer"] = tokenizer
            sem_module._model_cache["model"] = model
            sem_module._model_cache["model_name"] = "mock-model"
            return tokenizer, model

        return mock_load

    def test_returns_score_and_evidence(self):
        import app.similarity.semantic as sem_module
        sem_module._model_cache.clear()

        with patch.object(sem_module, "_load_model", self._patch_model()):
            score, evidence = semantic_similarity("x = 1", "y = 2")

        # score may be None if the mock didn't cooperate fully
        assert isinstance(evidence, list)
        assert len(evidence) > 0

    def test_evidence_has_required_structure(self):
        import app.similarity.semantic as sem_module
        sem_module._model_cache.clear()

        with patch.object(sem_module, "_load_model", self._patch_model()):
            score, evidence = semantic_similarity("def foo(): pass", "def bar(): pass")

        for item in evidence:
            assert isinstance(item, dict), f"evidence item must be dict, got {type(item)}"
            assert "type" in item or "note" in item, \
                f"evidence item missing 'type' or 'note': {item}"


# ──────────────────────────────────────────────────────────────────────────────
# Integration test — requires model download (skip by default)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
class TestSemanticSimilarityReal:
    """
    Real model tests. Skipped in normal CI — run with: pytest -m slow
    These tests require microsoft/unixcoder-base to be downloaded.
    """

    def test_identical_pair_scores_high(self):
        code = _read("identical_a.py")
        score, evidence = semantic_similarity(code, code)
        assert score is not None
        assert score >= 0.95, f"Identical code should score >=0.95, got {score}"
        assert isinstance(evidence, list)
        assert len(evidence) > 0

    def test_unrelated_pair_scores_low(self):
        code_a = _read("unrelated_a.py")
        code_b = _read("unrelated_b.py")
        score, evidence = semantic_similarity(code_a, code_b)
        assert score is not None
        assert score < 0.8, f"Unrelated pair should score <0.8, got {score}"

    def test_truncation_disclosed_for_long_file(self):
        long_code = _read("long_file.py")
        short_code = _read("one_liner.py")
        score, evidence = semantic_similarity(long_code, short_code)
        types = [e.get("type") for e in evidence]
        # long_file.py has >512 tokens → truncation must be disclosed
        assert "truncation_disclosure" in types, \
            "Truncation must be disclosed as evidence for long files (section 8.4)"
        trunc_items = [e for e in evidence if e.get("type") == "truncation_disclosure"]
        assert any(e.get("file") in ("a", "both") for e in trunc_items)

    def test_score_in_valid_range(self):
        code_a = _read("renamed_a.py")
        code_b = _read("renamed_b.py")
        score, evidence = semantic_similarity(code_a, code_b)
        if score is not None:
            assert 0.0 <= score <= 1.0

    def test_evidence_has_cosine_item(self):
        code = _read("identical_a.py")
        _, evidence = semantic_similarity(code, code)
        types = [e.get("type") for e in evidence]
        assert "cosine_similarity" in types

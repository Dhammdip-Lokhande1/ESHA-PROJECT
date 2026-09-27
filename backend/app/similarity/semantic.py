"""
similarity/semantic.py
=======================
Semantic similarity via UniXcoder (or GraphCodeBERT) cosine similarity.

Public API (section 8.4 of INSTRUCTIONS.md):

    semantic_similarity(code_a: str, code_b: str) -> tuple[float, list[dict]]

    Evidence MUST include:
      - The raw cosine value
      - A plain-language truncation note if either file exceeds 512 tokens
        (truncation must be DISCLOSED as evidence — never silently applied)
      - Token counts for each submission

Design decisions
----------------
* Model is LAZY-LOADED (loaded on first call, cached in _model_cache at
  module level). This avoids a ~2-3 GB model download blocking startup.
  The first call after a cold start will be slow — this is expected and
  documented.
* Default model: microsoft/unixcoder-base (lighter, good for deployment).
  Switch to microsoft/graphcodebert-base for evaluation/paper runs via the
  MODEL_NAME env var.
* MAX_TOKENS = 512 — the transformer's positional embedding limit.
  Longer code is TRUNCATED at the token level (truncation=True).
  When truncation occurs, an evidence item is added disclosing:
    - How many tokens the code actually produced
    - That analysis is based on the first ~N lines only
  This is the explicit requirement from section 8.4.
* Embeddings are computed with mean-pooling over the last hidden state
  (standard approach for code embedding similarity). We do NOT use the
  [CLS] token alone — it tends to carry less discriminative signal for
  code snippets than mean-pooling.
* CPU-only inference — torch.no_grad(), no GPU required (G6: zero cost).
* Thread safety: the model/tokenizer are loaded once and shared. The
  _load_model() function uses a simple lock to prevent double-loading
  under concurrent requests.

Non-Negotiable Rule 2: every call returns (score, evidence_list) —
a bare float reaching the API is a spec violation.
"""
from __future__ import annotations

import threading
from typing import Any

import torch
import torch.nn.functional as F

from app.config import settings

# ──────────────────────────────────────────────────────────────────────────────
# Model cache — lazy loaded on first call
# ──────────────────────────────────────────────────────────────────────────────
_model_cache: dict[str, Any] = {}
_model_lock = threading.Lock()

MAX_TOKENS = 512  # transformer positional limit


def _load_model() -> tuple[Any, Any]:
    """
    Lazy-load and cache the tokenizer and model.
    Thread-safe — uses a lock to prevent concurrent downloads.

    Returns
    -------
    (tokenizer, model) — both from HuggingFace transformers.
    """
    with _model_lock:
        if "tokenizer" not in _model_cache:
            from transformers import AutoModel, AutoTokenizer  # noqa: PLC0415

            model_name = settings.MODEL_NAME
            # Try loading from local cache first to avoid network check latency
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
                model = AutoModel.from_pretrained(model_name, local_files_only=True)
            except Exception:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModel.from_pretrained(model_name)

            model.eval()  # inference mode — no gradients needed
            _model_cache["tokenizer"] = tokenizer
            _model_cache["model"] = model
            _model_cache["model_name"] = model_name

        return _model_cache["tokenizer"], _model_cache["model"]


def _mean_pool(hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """
    Mean-pool the last hidden state, masked to actual tokens only
    (ignores padding positions).
    """
    # hidden_state: (batch, seq_len, hidden_dim)
    # attention_mask: (batch, seq_len) — 1 for real tokens, 0 for padding
    mask_expanded = attention_mask.unsqueeze(-1).float()
    sum_hidden = (hidden_state * mask_expanded).sum(dim=1)
    count = mask_expanded.sum(dim=1).clamp(min=1e-9)
    return sum_hidden / count


def _encode(code: str, tokenizer: Any) -> dict:
    """
    Tokenize *code* and return the encoding dict with token count info.

    Returns
    -------
    dict with keys:
      - input_ids, attention_mask  (tensors ready for the model)
      - raw_token_count            (tokens before any truncation)
      - was_truncated              (bool)
    """
    raw_ids = tokenizer.encode(code, add_special_tokens=True, truncation=False)
    raw_count = len(raw_ids)
    was_truncated = raw_count > MAX_TOKENS

    enc = tokenizer(
        code,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_TOKENS,
        padding=False,
        add_special_tokens=True,
    )
    enc["raw_token_count"] = raw_count
    enc["was_truncated"] = was_truncated
    return enc


def _build_semantic_evidence(
    cosine_score: float,
    raw_count_a: int,
    raw_count_b: int,
    was_truncated_a: bool,
    was_truncated_b: bool,
    model_name: str,
) -> list[dict[str, Any]]:
    """
    Build evidence list for semantic similarity.

    Always includes:
      1. Summary item with cosine value, model name, token counts
      2. Truncation disclosure items if either file was truncated
         (required by section 8.4 — truncation MUST be disclosed as evidence)
    """
    evidence: list[dict[str, Any]] = []

    evidence.append(
        {
            "type": "cosine_similarity",
            "value": round(cosine_score, 6),
            "model": model_name,
            "token_count_a": raw_count_a,
            "token_count_b": raw_count_b,
            "note": (
                f"Cosine similarity between mean-pooled embeddings "
                f"from {model_name}. "
                f"Submission A: {raw_count_a} tokens. "
                f"Submission B: {raw_count_b} tokens."
            ),
        }
    )

    if was_truncated_a:
        evidence.append(
            {
                "type": "truncation_disclosure",
                "file": "a",
                "raw_token_count": raw_count_a,
                "truncated_to": MAX_TOKENS,
                "note": (
                    f"Submission A has {raw_count_a} tokens, which exceeds the "
                    f"{MAX_TOKENS}-token limit. Analysis is based on the first "
                    f"~{MAX_TOKENS} tokens only (approximately the first "
                    f"{int(MAX_TOKENS * 0.75)} lines of code). "
                    f"Similarity may be underestimated if the key differences "
                    f"are in the truncated portion."
                ),
            }
        )

    if was_truncated_b:
        evidence.append(
            {
                "type": "truncation_disclosure",
                "file": "b",
                "raw_token_count": raw_count_b,
                "truncated_to": MAX_TOKENS,
                "note": (
                    f"Submission B has {raw_count_b} tokens, which exceeds the "
                    f"{MAX_TOKENS}-token limit. Analysis is based on the first "
                    f"~{MAX_TOKENS} tokens only (approximately the first "
                    f"{int(MAX_TOKENS * 0.75)} lines of code). "
                    f"Similarity may be underestimated if the key differences "
                    f"are in the truncated portion."
                ),
            }
        )

    if not was_truncated_a and not was_truncated_b:
        evidence.append(
            {
                "type": "truncation_disclosure",
                "file": "both",
                "note": (
                    f"No truncation applied — both submissions are within the "
                    f"{MAX_TOKENS}-token limit. Similarity is computed over the "
                    f"full code of both submissions."
                ),
            }
        )

    return evidence


def semantic_similarity(
    code_a: str,
    code_b: str,
) -> tuple[float | None, list[dict[str, Any]]]:
    """
    Compute cosine similarity between UniXcoder embeddings of two code snippets.

    Parameters
    ----------
    code_a, code_b : str
        Raw Python source code strings.

    Returns
    -------
    score : float | None
        Cosine similarity in [0.0, 1.0] (clamped — raw cosine can be slightly
        negative for very dissimilar embeddings but we clamp to 0 for UX
        consistency; full value is in evidence).
        Returns None if the model fails to load (rather than crashing the
        entire /analyze endpoint).
    evidence : list[dict]
        Always non-empty. Contains cosine value, model name, token counts, and
        truncation disclosures. NEVER returns a bare float (Rule 2).

    Notes
    -----
    Empty input: returns (0.0, evidence_noting_empty) — symmetric with
    lexical/structural modules.
    """
    # ── Handle empty inputs ────────────────────────────────────────────────
    if not code_a or not code_a.strip():
        return 0.0, [
            {
                "type": "empty_input",
                "file": "a",
                "note": "Submission A is empty — semantic similarity is 0.0.",
            }
        ]
    if not code_b or not code_b.strip():
        return 0.0, [
            {
                "type": "empty_input",
                "file": "b",
                "note": "Submission B is empty — semantic similarity is 0.0.",
            }
        ]

    # ── Load model (lazy) ──────────────────────────────────────────────────
    try:
        tokenizer, model = _load_model()
    except Exception as exc:
        return None, [
            {
                "type": "model_load_error",
                "error": str(exc),
                "note": (
                    "Model could not be loaded — semantic similarity unavailable. "
                    "Check MODEL_NAME in config and ensure the model is downloadable."
                ),
            }
        ]

    # ── Tokenize ───────────────────────────────────────────────────────────
    try:
        enc_a = _encode(code_a, tokenizer)
        enc_b = _encode(code_b, tokenizer)
    except Exception as exc:
        return None, [
            {
                "type": "tokenization_error",
                "error": str(exc),
                "note": "Tokenization failed — semantic similarity unavailable.",
            }
        ]

    # ── Compute embeddings ─────────────────────────────────────────────────
    try:
        with torch.no_grad():
            out_a = model(
                input_ids=enc_a["input_ids"],
                attention_mask=enc_a["attention_mask"],
            )
            out_b = model(
                input_ids=enc_b["input_ids"],
                attention_mask=enc_b["attention_mask"],
            )

        emb_a = _mean_pool(out_a.last_hidden_state, enc_a["attention_mask"])
        emb_b = _mean_pool(out_b.last_hidden_state, enc_b["attention_mask"])

        # L2-normalise then dot product = cosine similarity
        emb_a = F.normalize(emb_a, p=2, dim=1)
        emb_b = F.normalize(emb_b, p=2, dim=1)
        cosine_raw = (emb_a * emb_b).sum().item()

        # Clamp to [0, 1] — very dissimilar code can produce slightly negative
        # cosine; 0 is the natural floor for "not similar"
        score = float(max(0.0, min(1.0, cosine_raw)))

    except Exception as exc:
        return None, [
            {
                "type": "inference_error",
                "error": str(exc),
                "note": "Model inference failed — semantic similarity unavailable.",
            }
        ]

    # ── Build evidence ─────────────────────────────────────────────────────
    evidence = _build_semantic_evidence(
        cosine_score=cosine_raw,  # raw (pre-clamp) in evidence for full transparency
        raw_count_a=enc_a["raw_token_count"],
        raw_count_b=enc_b["raw_token_count"],
        was_truncated_a=enc_a["was_truncated"],
        was_truncated_b=enc_b["was_truncated"],
        model_name=_model_cache.get("model_name", settings.MODEL_NAME),
    )

    return round(score, 6), evidence

"""
similarity/lexical.py
======================
Lexical similarity via 3-gram Jaccard similarity.

Public API (section 8.2 of INSTRUCTIONS.md):

    lexical_similarity(
        tokens_a: list[str],
        tokens_b: list[str]
    ) -> tuple[float, list[dict]]

Non-Negotiable Rule 2: the returned evidence list is REQUIRED — a bare float
reaching the API layer is a spec violation.  Evidence here = the top matched
n-grams with their counts in each submission.

Algorithm
---------
1.  Build multisets of 3-grams from each token sequence.
2.  Jaccard on multisets = |A ∩ B| / |A ∪ B|, where intersection and union
    are computed as min/max of per-element counts.
3.  Evidence: top-N matched n-grams sorted by min-count descending,
    then any n-grams that appear in A but not B (and vice-versa) for
    a sense of what's unique.

Design notes
------------
* n=3 (trigrams) chosen per section 8.2 spec; exposed as a parameter for
  unit tests and future ablation.
* Multiset Jaccard rather than set Jaccard captures repeated patterns —
  a submission that copies the same block 3× should score higher than one
  that copies it once.
* Returns an empty evidence list (not None) if either token sequence is empty,
  paired with score=0.0.  This is intentional: callers can distinguish
  "truly zero overlap" from "evidence unavailable" because the evidence list
  will still be present (just empty).
"""
from __future__ import annotations

from collections import Counter
from typing import Any


def _build_ngrams(tokens: list[str], n: int) -> Counter[tuple[str, ...]]:
    """Return a Counter of n-gram tuples from *tokens*."""
    if len(tokens) < n:
        # Return the tokens as 1-grams if shorter than n;
        # this prevents a silent 0 when both files are short and identical.
        return Counter(tuple(tokens[i : i + 1]) for i in range(len(tokens)))
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def _multiset_jaccard(counter_a: Counter, counter_b: Counter) -> float:
    """
    Jaccard similarity for two multisets represented as Counters.
    |A ∩ B| / |A ∪ B|  where ∩ = min, ∪ = max element-wise.
    """
    if not counter_a and not counter_b:
        return 1.0  # both empty → identical (by convention)
    if not counter_a or not counter_b:
        return 0.0

    keys = set(counter_a) | set(counter_b)
    intersection = sum(min(counter_a[k], counter_b[k]) for k in keys)
    union = sum(max(counter_a[k], counter_b[k]) for k in keys)
    return intersection / union if union > 0 else 0.0


def _build_evidence(
    counter_a: Counter,
    counter_b: Counter,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """
    Build the evidence list for lexical similarity.

    Each evidence item is a dict with:
      - ngram:     the token n-gram as a space-joined string
      - count_a:   occurrences in submission A
      - count_b:   occurrences in submission B
      - status:    'matched' | 'only_in_a' | 'only_in_b'

    The evidence is ordered by:
      1. Matched items (both A and B), sorted by min-count desc (strongest matches first)
      2. Items only in A (sorted by count_a desc)
      3. Items only in B (sorted by count_b desc)

    Top-N matched items are included; the rest are summarised as a count.
    """
    evidence: list[dict[str, Any]] = []
    all_keys = set(counter_a) | set(counter_b)

    matched = []
    only_a = []
    only_b = []

    for key in all_keys:
        ca = counter_a[key]
        cb = counter_b[key]
        if ca > 0 and cb > 0:
            matched.append(
                {
                    "ngram": " ".join(key),
                    "count_a": ca,
                    "count_b": cb,
                    "status": "matched",
                }
            )
        elif ca > 0:
            only_a.append(
                {
                    "ngram": " ".join(key),
                    "count_a": ca,
                    "count_b": 0,
                    "status": "only_in_a",
                }
            )
        else:
            only_b.append(
                {
                    "ngram": " ".join(key),
                    "count_a": 0,
                    "count_b": cb,
                    "status": "only_in_b",
                }
            )

    matched.sort(key=lambda x: min(x["count_a"], x["count_b"]), reverse=True)
    only_a.sort(key=lambda x: x["count_a"], reverse=True)
    only_b.sort(key=lambda x: x["count_b"], reverse=True)

    # Include top_n matched items
    evidence.extend(matched[:top_n])

    # Summarise any additional matched items we're not listing explicitly
    if len(matched) > top_n:
        evidence.append(
            {
                "ngram": "<summary>",
                "count_a": None,
                "count_b": None,
                "status": "additional_matched_count",
                "additional_matched": len(matched) - top_n,
            }
        )

    # Include up to top_n/2 unmatched items each side for diagnostic value
    half = max(top_n // 2, 3)
    evidence.extend(only_a[:half])
    evidence.extend(only_b[:half])

    return evidence


def lexical_similarity(
    tokens_a: list[str],
    tokens_b: list[str],
    n: int = 3,
    top_n: int = 10,
) -> tuple[float, list[dict[str, Any]]]:
    """
    Compute 3-gram (default) Jaccard similarity between two token sequences.

    Parameters
    ----------
    tokens_a, tokens_b : list[str]
        Output of ``preprocessing.preprocess.tokenize_code``.
    n : int
        N-gram size.  Default 3 per spec; exposed for testing/ablation.
    top_n : int
        Number of top matched n-grams to include in evidence.

    Returns
    -------
    score : float
        Jaccard similarity in [0.0, 1.0].
    evidence : list[dict]
        Evidence items — see _build_evidence docstring.
        NEVER returns a bare float without this list (Non-Negotiable Rule 2).
    """
    if not tokens_a and not tokens_b:
        score = 1.0
        evidence: list[dict] = [
            {
                "ngram": "<summary>",
                "count_a": 0,
                "count_b": 0,
                "status": "both_empty",
                "note": "Both token sequences are empty — identical by convention.",
            }
        ]
        return score, evidence

    if not tokens_a or not tokens_b:
        score = 0.0
        evidence = [
            {
                "ngram": "<summary>",
                "count_a": len(tokens_a),
                "count_b": len(tokens_b),
                "status": "one_empty",
                "note": "One submission produced no tokens — score is 0.0.",
            }
        ]
        return score, evidence

    counter_a = _build_ngrams(tokens_a, n)
    counter_b = _build_ngrams(tokens_b, n)

    score = _multiset_jaccard(counter_a, counter_b)
    evidence = _build_evidence(counter_a, counter_b, top_n=top_n)

    return round(score, 6), evidence

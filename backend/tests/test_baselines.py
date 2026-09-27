"""
backend/tests/test_baselines.py
============================================================
Unit tests for Normalized Token Baseline and External Adapters.
"""

import unittest
from experiments.baselines import (
    normalized_token_baseline,
    unixcoder_cosine,
    get_normalized_tokens,
)


class TestExternalBaselines(unittest.TestCase):
    def test_normalized_token_baseline_identifier_renaming(self):
        """Test normalized token baseline produces score 1.0 for renamed variables."""
        code_a = "def compute(a, b):\n    total = a + b\n    return total\n"
        code_b = "def compute(x, y):\n    result = x + y\n    return result\n"

        tokens_a = get_normalized_tokens(code_a)
        tokens_b = get_normalized_tokens(code_b)
        self.assertEqual(tokens_a, tokens_b)

        score = normalized_token_baseline(code_a, code_b)
        self.assertEqual(score, 1.0)

    def test_normalized_token_baseline_unrelated_code(self):
        """Test normalized token baseline produces low score for unrelated code."""
        code_a = "for i in range(10):\n    print(i)\n"
        code_b = "import math\nx = math.sin(3.14)\n"

        score = normalized_token_baseline(code_a, code_b)
        self.assertLess(score, 0.5)

    def test_unixcoder_cosine_embedding_cached(self):
        """Test UniXcoder cosine similarity calculation."""
        code_a = "x = 10\n"
        code_b = "x = 10\n"
        score = unixcoder_cosine(code_a, code_b)
        self.assertAlmostEqual(score, 1.0, places=4)


if __name__ == "__main__":
    unittest.main()

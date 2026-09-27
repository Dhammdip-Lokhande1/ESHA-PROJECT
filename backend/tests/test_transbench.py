"""
backend/tests/test_transbench.py
============================================================
Unit tests for TransBench-Lite Dataset & Leakage Assertions.
"""

import unittest
import ast
import json
from pathlib import Path
import pandas as pd

from experiments.build_transbench_lite import (
    apply_formatting_change,
    apply_variable_renaming,
    apply_structural_refactoring,
    apply_dead_code_insertion,
    apply_combined,
    METADATA_JSON,
    OUT_DIR,
)


class TestTransBenchLite(unittest.TestCase):
    def test_transbench_leakage_assertion(self):
        """Test problem_id split disjointness assertion (Zero Data Leakage)."""
        with open(METADATA_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)

        train_pids = set(meta["train_problem_ids"])
        test_pids = set(meta["test_problem_ids"])

        # Assertion must hold
        self.assertTrue(train_pids.isdisjoint(test_pids))
        self.assertEqual(len(train_pids & test_pids), 0)

    def test_ast_transformations_valid_python(self):
        """Test that all AST transformations produce valid Python that parses."""
        sample_code = (
            "def calculate_sum(a, b):\n"
            "    total = a + b\n"
            "    if total > 10:\n"
            "        print('Large')\n"
            "    else:\n"
            "        print('Small')\n"
            "    return total\n"
        )

        t_fmt = apply_formatting_change(sample_code)
        t_var = apply_variable_renaming(sample_code)
        t_struct = apply_structural_refactoring(sample_code)
        t_dead = apply_dead_code_insertion(sample_code)
        t_comb = apply_combined(sample_code)

        for name, trans_code in [
            ("formatting", t_fmt),
            ("variable_renaming", t_var),
            ("structural_refactoring", t_struct),
            ("dead_code", t_dead),
            ("combined", t_comb),
        ]:
            try:
                ast.parse(trans_code)
            except SyntaxError as e:
                self.fail(f"Transformation '{name}' produced invalid Python: {e}")

    def test_pairs_csv_structure_and_counts(self):
        """Test generated pairs.csv schema if it exists."""
        csv_path = OUT_DIR / "pairs.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            required_cols = [
                "pair_id", "split", "code_a_path", "code_b_path",
                "label", "transformation_label", "negative_type", "problem_id"
            ]
            for col in required_cols:
                self.assertIn(col, df.columns)

            self.assertIn("train", df["split"].values)
            self.assertIn("test", df["split"].values)


if __name__ == "__main__":
    unittest.main()

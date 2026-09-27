"""
fixtures/long_file.py
A long Python file with >512 tokens — tests the token-truncation path in semantic
similarity (M2) and ensures tokenize/AST don't break on large inputs.
"""
from typing import Optional


class DataProcessor:
    """A data processing class with many methods to generate lots of tokens."""

    def __init__(self, data: list, config: Optional[dict] = None):
        self.data = data
        self.config = config or {}
        self.results: list = []
        self.errors: list = []
        self._cache: dict = {}

    def validate_input(self, item) -> bool:
        if item is None:
            self.errors.append({"item": item, "reason": "null_value"})
            return False
        if not isinstance(item, (int, float, str, list, dict)):
            self.errors.append({"item": item, "reason": "unsupported_type"})
            return False
        return True

    def preprocess_item(self, item):
        if isinstance(item, str):
            item = item.strip().lower()
        elif isinstance(item, list):
            item = [x for x in item if x is not None]
        elif isinstance(item, dict):
            item = {k: v for k, v in item.items() if v is not None}
        return item

    def process_item(self, item):
        if not self.validate_input(item):
            return None
        preprocessed = self.preprocess_item(item)
        cache_key = str(preprocessed)
        if cache_key in self._cache:
            return self._cache[cache_key]
        result = self._compute(preprocessed)
        self._cache[cache_key] = result
        return result

    def _compute(self, item):
        if isinstance(item, (int, float)):
            return item * 2
        elif isinstance(item, str):
            return item[::-1]
        elif isinstance(item, list):
            return sorted(item)
        elif isinstance(item, dict):
            return dict(sorted(item.items()))
        return item

    def process_all(self):
        self.results = []
        for item in self.data:
            result = self.process_item(item)
            if result is not None:
                self.results.append(result)
        return self.results

    def get_summary(self) -> dict:
        return {
            "total_input": len(self.data),
            "total_processed": len(self.results),
            "total_errors": len(self.errors),
            "error_rate": len(self.errors) / max(len(self.data), 1),
            "cache_size": len(self._cache),
        }

    def reset(self):
        self.results = []
        self.errors = []
        self._cache = {}

    def filter_results(self, predicate) -> list:
        return [r for r in self.results if predicate(r)]

    def map_results(self, transform) -> list:
        return [transform(r) for r in self.results]

    def reduce_results(self, accumulator, initial=None):
        result = initial
        for item in self.results:
            result = accumulator(result, item)
        return result

    def chunk_results(self, size: int) -> list:
        return [
            self.results[i : i + size]
            for i in range(0, len(self.results), size)
        ]

    def export_results(self, fmt: str = "list"):
        if fmt == "list":
            return list(self.results)
        elif fmt == "dict":
            return {i: v for i, v in enumerate(self.results)}
        elif fmt == "set":
            try:
                return set(self.results)
            except TypeError:
                return set()
        raise ValueError(f"Unsupported format: {fmt}")

    def merge(self, other: "DataProcessor"):
        combined_data = self.data + other.data
        return DataProcessor(combined_data, self.config)

    def __repr__(self) -> str:
        return (
            f"DataProcessor("
            f"data_size={len(self.data)}, "
            f"results_size={len(self.results)}, "
            f"errors={len(self.errors)})"
        )

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self):
        return iter(self.results)

    def __contains__(self, item) -> bool:
        return item in self.results

    def __add__(self, other: "DataProcessor") -> "DataProcessor":
        return self.merge(other)


def create_processor(data: list, **kwargs) -> DataProcessor:
    config = {
        "strict": kwargs.get("strict", False),
        "cache_enabled": kwargs.get("cache_enabled", True),
        "max_errors": kwargs.get("max_errors", 100),
    }
    return DataProcessor(data, config)


def batch_process(datasets: list[list], **kwargs) -> list[DataProcessor]:
    processors = [create_processor(ds, **kwargs) for ds in datasets]
    for p in processors:
        p.process_all()
    return processors


def aggregate_summaries(processors: list[DataProcessor]) -> dict:
    if not processors:
        return {}
    total_input = sum(p.get_summary()["total_input"] for p in processors)
    total_processed = sum(p.get_summary()["total_processed"] for p in processors)
    total_errors = sum(p.get_summary()["total_errors"] for p in processors)
    return {
        "batch_size": len(processors),
        "total_input": total_input,
        "total_processed": total_processed,
        "total_errors": total_errors,
        "overall_error_rate": total_errors / max(total_input, 1),
    }

import heapq
from typing import List

def merge_sorted(l1: List[int], l2: List[int]) -> List[int]:
    """Merge sorted iterables using heapq.merge."""
    return list(heapq.merge(l1, l2))

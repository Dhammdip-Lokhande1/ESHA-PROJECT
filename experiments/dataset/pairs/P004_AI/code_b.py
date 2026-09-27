import bisect
from typing import List

def search(arr: List[int], target: int) -> int:
    """Perform binary search using Python stdlib bisect module."""
    idx = bisect.bisect_left(arr, target)
    return idx if idx < len(arr) and arr[idx] == target else -1

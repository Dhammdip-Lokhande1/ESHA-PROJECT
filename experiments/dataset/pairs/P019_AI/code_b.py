from typing import Tuple, List

def find_indices(arr: List[int], target: int) -> Tuple[int, int]:
    """Find first and last occurrences of target using list indexing."""
    if target not in arr:
        return (-1, -1)
    first = arr.index(target)
    last = len(arr) - 1 - arr[::-1].index(target)
    return (first, last)

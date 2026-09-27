from typing import List, Any

def flatten(nested_list: List[Any]) -> List[Any]:
    """Generator-based recursive flattening function."""
    def _gen(lst):
        for elem in lst:
            if isinstance(elem, list):
                yield from _gen(elem)
            else:
                yield elem
    return list(_gen(nested_list))

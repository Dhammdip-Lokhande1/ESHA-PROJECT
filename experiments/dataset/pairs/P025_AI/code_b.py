from typing import List, Any

def remove_duplicates(items: List[Any]) -> List[Any]:
    """Remove duplicates maintaining insertion order using dict.fromkeys."""
    return list(dict.fromkeys(items))

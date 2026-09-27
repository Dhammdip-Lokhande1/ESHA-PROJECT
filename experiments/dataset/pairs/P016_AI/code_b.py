import itertools
from typing import List, Tuple

def rle_encode(s: str) -> List[Tuple[str, int]]:
    """Run-length encode string using itertools.groupby."""
    return [(char, len(list(group))) for char, group in itertools.groupby(s)]

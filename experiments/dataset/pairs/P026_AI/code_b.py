import os
from typing import List

def longest_common_prefix(strs: List[str]) -> str:
    """Compute longest common prefix using os.path.commonprefix."""
    return os.path.commonprefix(strs)

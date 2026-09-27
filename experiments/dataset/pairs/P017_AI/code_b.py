from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TreeNode:
    val: int = 0
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None

def count_nodes(vals: List[int]) -> int:
    """Count tree nodes initialized from values."""
    return len([TreeNode(v) for v in vals])

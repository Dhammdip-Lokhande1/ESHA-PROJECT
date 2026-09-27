from typing import List

def transpose(matrix: List[List[int]]) -> List[List[int]]:
    """Transpose matrix using Pythonic zip unpacked composition."""
    return [list(row) for row in zip(*matrix)]

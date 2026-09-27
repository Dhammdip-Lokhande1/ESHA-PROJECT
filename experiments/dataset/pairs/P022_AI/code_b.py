from typing import List

def pascal_triangle(n: int) -> List[List[int]]:
    """Generate Pascal's triangle using iterative row expansion."""
    rows = []
    for _ in range(n):
        row = [1]
        if rows:
            last = rows[-1]
            row.extend([a + b for a, b in zip(last[:-1], last[1:])])
            row.append(1)
        rows.append(row)
    return rows

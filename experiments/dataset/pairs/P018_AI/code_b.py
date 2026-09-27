from collections import deque
from typing import Any, List

class Stack:
    """Efficient stack wrapper around collections.deque."""
    def __init__(self):
        self._data = deque()
    def push(self, item: Any) -> None:
        self._data.append(item)
    def pop(self) -> Any:
        return self._data.pop() if self._data else None

def run_stack() -> List[int]:
    stk = Stack()
    for v in (10, 20, 30):
        stk.push(v)
    return [stk.pop() for _ in range(3)]

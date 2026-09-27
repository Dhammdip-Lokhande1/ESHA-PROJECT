from collections import deque
from typing import List, Any

class Queue:
    """FIFO Queue implementation using collections.deque."""
    def __init__(self):
        self._dq = deque()
    def enqueue(self, item: Any) -> None:
        self._dq.append(item)
    def dequeue(self) -> Any:
        return self._dq.popleft() if self._dq else None

def run_queue() -> List[int]:
    q = Queue()
    for item in (10, 20, 30):
        q.enqueue(item)
    return [q.dequeue() for _ in range(3)]

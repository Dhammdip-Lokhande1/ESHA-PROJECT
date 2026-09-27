class Queue:
    def __init__(self):
        self.items = []
    def enqueue(self, item):
        self.items.insert(0, item)
    def dequeue(self):
        return self.items.pop() if self.items else None

def run_queue():
    q = Queue()
    for val in [10, 20, 30]:
        q.enqueue(val)
    res = []
    while q.items:
        res.append(q.dequeue())
    return res

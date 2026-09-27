class Stack:
    # LIFO stack implementation
    def __init__(self):
        self.items = []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        return self.items.pop() if self.items else None

def run_stack():
    s = Stack()
    s.push(10)
    s.push(20)
    s.push(30)
    res = []
    res.append(s.pop())
    res.append(s.pop())
    res.append(s.pop())
    return res

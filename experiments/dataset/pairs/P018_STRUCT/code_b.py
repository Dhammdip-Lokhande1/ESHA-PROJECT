class Stack:
    def __init__(self):
        self.items = []
    def push(self, item):
        self.items.insert(0, item)
    def pop(self):
        return self.items.pop(0) if self.items else None

def run_stack():
    s = Stack()
    s.push(10)
    s.push(20)
    s.push(30)
    return [s.pop(), s.pop(), s.pop()]

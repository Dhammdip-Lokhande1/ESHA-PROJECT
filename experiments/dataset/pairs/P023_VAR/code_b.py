class FifoQueueContainer:
    def __init__(self):
        self.element_list = []
    def enqueue(self, val):
        self.element_list.append(val)
    def dequeue(self):
        return self.element_list.pop(0) if self.element_list else None

def run_queue():
    q_obj = FifoQueueContainer()
    q_obj.enqueue(10)
    q_obj.enqueue(20)
    q_obj.enqueue(30)
    return [q_obj.dequeue(), q_obj.dequeue(), q_obj.dequeue()]

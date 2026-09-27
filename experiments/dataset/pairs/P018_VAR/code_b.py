class CustomLifoBuffer:
    def __init__(self):
        self.storage_container = []
    def push(self, element):
        self.storage_container.append(element)
    def pop(self):
        return self.storage_container.pop() if self.storage_container else None

def run_stack():
    buf = CustomLifoBuffer()
    buf.push(10)
    buf.push(20)
    buf.push(30)
    output_log = []
    output_log.append(buf.pop())
    output_log.append(buf.pop())
    output_log.append(buf.pop())
    return output_log

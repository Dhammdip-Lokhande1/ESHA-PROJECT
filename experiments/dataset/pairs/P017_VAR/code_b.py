class NodeElement:
    def __init__(self, value=0, left_child=None, right_child=None):
        self.val = value
        self.left = left_child
        self.right = right_child

def count_nodes(value_list):
    if not value_list:
        return 0
    allocated_nodes = [NodeElement(item) for item in value_list]
    return len(allocated_nodes)

class TreeNode:
    def __init__(self, val=0):
        self.val = val

def count_nodes(vals):
    total = 0
    for v in vals:
        n = TreeNode(v)
        total += 1
    return total

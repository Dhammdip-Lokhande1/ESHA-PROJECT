class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def count_nodes(vals):
    if not vals:
        return 0
    nodes = [TreeNode(v) for v in vals]
    return len(nodes)

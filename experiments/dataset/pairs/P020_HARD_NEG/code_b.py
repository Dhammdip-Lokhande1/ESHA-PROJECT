def count_nodes(root):
    # Tree max depth counter (hard negative: recursive node traversal, depth scalar return)
    if root is None:
        return 0
    left_depth = count_nodes(root.left)
    right_depth = count_nodes(root.right)
    return 1 + max(left_depth, right_depth)

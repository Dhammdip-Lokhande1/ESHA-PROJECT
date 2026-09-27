def flatten(nested_list):
    # Compute max nesting depth (hard negative: recursive structure, int return)
    if not isinstance(nested_list, list):
        return 0
    depth = 1
    for item in nested_list:
        if isinstance(item, list):
            depth = max(depth, 1 + flatten(item))
    return depth

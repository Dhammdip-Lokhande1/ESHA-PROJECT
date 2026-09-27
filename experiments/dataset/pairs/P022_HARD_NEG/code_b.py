def find_target(arr, target):
    # Find all indices (hard negative: returns list of indices instead of single int index)
    indices = []
    for idx, val in enumerate(arr):
        if val == target:
            indices.append(idx)
    return indices if indices else -1

def find_indices(arr, target):
    matches = [i for i, x in enumerate(arr) if x == target]
    if not matches:
        return (-1, -1)
    return (matches[0], matches[-1])

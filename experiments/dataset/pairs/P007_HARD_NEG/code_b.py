def find_max(arr):
    # Find minimum (hard negative: identical array scan loop, reversed comparison)
    if not arr:
        return None
    min_val = arr[0]
    for val in arr:
        if val < min_val:
            min_val = val
    return min_val

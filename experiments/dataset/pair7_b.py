def find_max(arr):
    if not arr: return None
    max_val = arr[0]
    for val in arr:
        if val > max_val:
            max_val = val
    return max_val
# exactly the same
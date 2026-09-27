def find_max(arr):
    if not arr:
        return None
    sorted_items = sorted(arr)
    return sorted_items[-1]

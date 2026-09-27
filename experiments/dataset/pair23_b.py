def find_max(arr):
    if not arr: return None
    arr_sorted = sorted(arr)
    return arr_sorted[-1]
def search(arr, x, l=0, r=None):
    if r is None: r = len(arr) - 1
    if l > r: return -1
    mid = (l + r) // 2
    if arr[mid] == x: return mid
    if arr[mid] > x: return search(arr, x, l, mid - 1)
    return search(arr, x, mid + 1, r)
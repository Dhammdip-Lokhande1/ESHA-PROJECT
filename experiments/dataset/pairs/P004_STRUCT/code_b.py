def search(arr, target, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    if left > right:
        return -1
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    if arr[mid] > target:
        return search(arr, target, left, mid - 1)
    return search(arr, target, mid + 1, right)

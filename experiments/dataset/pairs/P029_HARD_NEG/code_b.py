def binary_search(arr, target, left=0, right=None):
    # Recursive linear search (hard negative: recursive signature, O(N) scan)
    if right is None:
        right = len(arr) - 1
    if left > right:
        return -1
    if arr[left] == target:
        return left
    return binary_search(arr, target, left + 1, right)

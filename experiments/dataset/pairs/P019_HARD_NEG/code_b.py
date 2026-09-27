def find_indices(arr, target):
    # Binary search approach (hard negative: returns (first_occurrence, count) instead of (first, last) index, assuming sorted array)
    left, right = 0, len(arr) - 1
    first = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            first = mid
            right = mid - 1
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    count = arr.count(target) if first != -1 else 0
    return (first, count)

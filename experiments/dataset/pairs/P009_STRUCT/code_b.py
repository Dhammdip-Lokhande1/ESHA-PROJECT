def sum_elements(arr):
    if not arr:
        return 0
    return arr[0] + sum_elements(arr[1:])

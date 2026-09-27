def find_indices(arr, target):
    # Finds first and last index of target in list
    first = -1
    last = -1
    for i in range(len(arr)):
        if arr[i] == target:
            if first == -1:
                first = i
            last = i
    return (first, last)

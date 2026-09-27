def find_indices(arr, target):
    first = -1
    last = -1
    for i in range(len(arr)):
        if arr[i] == target:
            if first == -1:
                first = i
            last = i
    return (first, last)

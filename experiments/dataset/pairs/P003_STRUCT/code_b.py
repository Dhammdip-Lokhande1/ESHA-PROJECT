def sort_array(arr):
    swapped = True
    while swapped:
        swapped = False
        for idx in range(len(arr) - 1):
            if arr[idx] > arr[idx + 1]:
                arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
                swapped = True
    return arr

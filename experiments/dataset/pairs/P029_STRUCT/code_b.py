def selection_sort(arr):
    res = []
    temp = list(arr)
    while temp:
        min_val = min(temp)
        res.append(min_val)
        temp.remove(min_val)
    return res

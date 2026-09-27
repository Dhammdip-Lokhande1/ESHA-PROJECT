def insertion_sort(arr):
    res = []
    for item in arr:
        inserted = False
        for idx in range(len(res)):
            if res[idx] > item:
                res.insert(idx, item)
                inserted = True
                break
        if not inserted:
            res.append(item)
    return res

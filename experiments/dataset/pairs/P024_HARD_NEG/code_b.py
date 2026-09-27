def merge_sorted(l1, l2):
    # Sorted intersection (hard negative: two pointers on two lists, but returns common elements instead of merged union)
    i, j = 0, 0
    res = []
    while i < len(l1) and j < len(l2):
        if l1[i] == l2[j]:
            res.append(l1[i])
            i += 1
            j += 1
        elif l1[i] < l2[j]:
            i += 1
        else:
            j += 1
    return res

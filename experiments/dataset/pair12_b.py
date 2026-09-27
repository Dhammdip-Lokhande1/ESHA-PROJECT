def bsearch(data, target):
    left = 0
    right = len(data) - 1
    while left <= right:
        m = (left + right) // 2
        if data[m] < target:
            left = m + 1
        elif data[m] > target:
            right = m - 1
        else:
            return m
    return -1
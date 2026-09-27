def my_sort(data):
    size = len(data)
    for a in range(size):
        for b in range(0, size-a-1):
            if data[b] > data[b+1]:
                data[b], data[b+1] = data[b+1], data[b]
    return data
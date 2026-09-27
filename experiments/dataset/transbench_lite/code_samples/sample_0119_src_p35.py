while True:
    try:
        row = list(map(int, input().split(',')))
        l = row[:10]
        v1, v2 = row[10], row[11]
        t = sum(l) / (v1 + v2)
        pos = v1 * t
        s = 0
        for i in range(10):
            s += l[i]
            if s >= pos:
                print(i + 1)
                break
    except:
        break
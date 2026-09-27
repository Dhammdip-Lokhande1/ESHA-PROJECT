import sys
for line in sys.stdin:
    try:
        v = list(map(int, line.split(',')))
        if len(v) < 12:
            continue
        dists = v[:10]
        s1, s2 = (v[10], v[11])
        cross = sum(dists) * s1 / (s1 + s2)
        acc = 0
        for i, length in enumerate(dists, 1):
            acc += length
            if acc >= cross:
                print(i)
                break
    except:
        break
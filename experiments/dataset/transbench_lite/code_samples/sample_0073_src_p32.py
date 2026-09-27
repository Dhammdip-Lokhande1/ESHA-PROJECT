import sys
for line in sys.stdin:
    w = int(line)
    res = []
    for i in range(10):
        if (w >> i) & 1:
            res.append(1 << i)
    print(*res)
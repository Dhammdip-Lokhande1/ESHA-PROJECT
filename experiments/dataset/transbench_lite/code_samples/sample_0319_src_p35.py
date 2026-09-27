import sys
for l in sys.stdin.read().splitlines():
    if not l.strip(): continue
    p = list(map(int, l.split(',')))
    tot = sum(p[:10])
    x = tot * p[10] / (p[10] + p[11])
    c = 0
    for i in range(10):
        c += p[i]
        if c >= x:
            print(i + 1)
            break
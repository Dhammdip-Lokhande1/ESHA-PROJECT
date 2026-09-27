import sys
for l in sys.stdin.read().split():
    d = int(l)
    res = 0
    for i in range(1, 600 // d):
        res += (i * d) ** 2 * d
    print(res)
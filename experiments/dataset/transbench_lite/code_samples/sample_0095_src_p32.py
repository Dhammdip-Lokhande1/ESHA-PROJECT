import sys
lines = sys.stdin.read().split()
for s in lines:
    val = int(s)
    res = [1 << i for i in range(10) if (val >> i) & 1]
    print(' '.join(map(str, res)))
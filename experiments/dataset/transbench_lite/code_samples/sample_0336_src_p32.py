import sys
for line in sys.stdin.read().split():
    w = int(line)
    ans = [2**i for i in range(10) if (w & (1 << i))]
    print(' '.join(map(str, ans)))
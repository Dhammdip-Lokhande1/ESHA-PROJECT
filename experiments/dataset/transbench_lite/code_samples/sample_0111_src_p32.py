import sys
for l in sys.stdin:
    w = int(l)
    ans = []
    for i in range(10):
        if w & (1 << i):
            ans.append(str(1 << i))
    print(' '.join(ans))
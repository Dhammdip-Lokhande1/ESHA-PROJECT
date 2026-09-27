import sys
for l in sys.stdin:
    n = int(l)
    cnt = 0
    for i in range(10):
        for j in range(10):
            for k in range(10):
                m = n - i - j - k
                if 0 <= m <= 9: cnt += 1
    print(cnt)
import sys
for line in sys.stdin:
    n = int(line)
    ans = 0
    for a in range(10):
        for b in range(10):
            for c in range(10):
                for d in range(10):
                    if a + b + c + d == n:
                        ans += 1
    print(ans)
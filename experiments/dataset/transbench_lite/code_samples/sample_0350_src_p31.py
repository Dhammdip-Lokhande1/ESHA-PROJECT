import sys
def solve(n, s, start):
    if n == 0:
        return 1 if s == 0 else 0
    ans = 0
    for i in range(start, 10):
        if i > s: break
        ans += solve(n - 1, s - i, i + 1)
    return ans
for line in sys.stdin:
    n, s = map(int, line.split())
    if n == 0 and s == 0: break
    print(solve(n, s, 0))
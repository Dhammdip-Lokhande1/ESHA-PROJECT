import sys
data = sys.stdin.read().split()
if data:
    p = [int(x) for x in data]
    n = len(p) - 1
    dp = [[0] * n for _ in range(n)]
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            dp[i][j] = min((dp[i][k] + dp[k + 1][j] + p[i] * p[k + 1] * p[j + 1] for k in range(i, j)))
    print(dp[0][n - 1])
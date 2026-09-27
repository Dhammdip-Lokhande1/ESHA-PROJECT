import sys
# Matrix Chain Multiplication DP
for line in sys.stdin:
    dims = list(map(int, line.split()))
    n = len(dims) - 1
    dp = [[0]*n for _ in range(n)]
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            dp[i][j] = min(dp[i][k] + dp[k+1][j] + dims[i]*dims[k+1]*dims[j+1] for k in range(i, j))
    print(dp[0][n-1])
import sys
for line in sys.stdin.read().splitlines():
    if not line.strip(): continue
    arr = [int(x) for x in line.split()]
    n = len(arr) - 1
    dp = [[0]*n for _ in range(n)]
    for L in range(2, n + 1):
        for i in range(n - L + 1):
            j = i + L - 1
            dp[i][j] = min(dp[i][k] + dp[k+1][j] + arr[i]*arr[k+1]*arr[j+1] for k in range(i, j))
    print(dp[0][n-1])
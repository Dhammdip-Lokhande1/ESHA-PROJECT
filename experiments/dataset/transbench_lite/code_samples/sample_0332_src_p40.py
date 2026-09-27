while True:
    try:
        p = [int(x) for x in input().split()]
        n = len(p) - 1
        dp = [[0]*n for _ in range(n)]
        for L in range(2, n + 1):
            for i in range(n - L + 1):
                j = i + L - 1
                dp[i][j] = float('inf')
                for k in range(i, j):
                    q = dp[i][k] + dp[k+1][j] + p[i]*p[k+1]*p[j+1]
                    if q < dp[i][j]: dp[i][j] = q
        print(dp[0][n-1])
    except:
        break
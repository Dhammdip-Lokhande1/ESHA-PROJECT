import sys
for line in sys.stdin:
    p = list(map(int, line.split()))
    n = len(p) - 1
    cost = [[0]*n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            cost[i][j] = min(cost[i][k] + cost[k+1][j] + p[i]*p[k+1]*p[j+1] for k in range(i, j))
    print(cost[0][n-1])
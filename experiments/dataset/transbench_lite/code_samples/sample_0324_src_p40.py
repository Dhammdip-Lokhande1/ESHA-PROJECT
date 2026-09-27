import sys
def matrix_chain_order(p):
    n = len(p) - 1
    m = [[0] * n for _ in range(n)]
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            m[i][j] = min(m[i][k] + m[k+1][j] + p[i]*p[k+1]*p[j+1] for k in range(i, j))
    return m[0][n-1]
for line in sys.stdin:
    if not line.strip(): continue
    p = list(map(int, line.split()))
    print(matrix_chain_order(p))
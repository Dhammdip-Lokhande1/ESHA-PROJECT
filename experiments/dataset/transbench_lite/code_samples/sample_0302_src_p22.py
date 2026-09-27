import sys
n = int(input())
for _ in range(n):
    x1, y1, x2, y2, x3, y3, x4, y4 = map(float, input().split())
    dx1 = x2 - x1; dy1 = y2 - y1
    dx2 = x4 - x3; dy2 = y4 - y3
    if abs(dx1 * dy2 - dy1 * dx2) < 1e-10:
        print('YES')
    else:
        print('NO')
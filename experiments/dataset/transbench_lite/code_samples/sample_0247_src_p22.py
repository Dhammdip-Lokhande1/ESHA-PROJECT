import sys
lines = sys.stdin.read().split()
if lines:
    n = int(lines[0])
    for i in range(n):
        x1, y1, x2, y2, x3, y3, x4, y4 = map(float, lines[1+8*i:9+8*i])
        cross = (x2 - x1)*(y4 - y3) - (y2 - y1)*(x4 - x3)
        print('YES' if abs(cross) < 1e-9 else 'NO')
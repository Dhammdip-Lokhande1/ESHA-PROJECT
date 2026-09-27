for _ in range(int(input())):
    ax, ay, bx, by, cx, cy, dx, dy = map(float, input().split())
    v1x, v1y = bx - ax, by - ay
    v2x, v2y = dx - cx, dy - cy
    print('YES' if abs(v1x*v2y - v1y*v2x) < 1e-9 else 'NO')
import sys
t = int(sys.stdin.readline())
for _ in range(t):
    pts = [float(x) for x in sys.stdin.readline().split()]
    dx1, dy1 = pts[2]-pts[0], pts[3]-pts[1]
    dx2, dy2 = pts[6]-pts[4], pts[7]-pts[5]
    print('YES' if abs(dx1*dy2 - dy1*dx2) < 1e-8 else 'NO')
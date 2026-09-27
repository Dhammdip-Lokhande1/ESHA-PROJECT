import math, sys
lines = sys.stdin.read().split()
if lines:
    n = int(lines[0])
    for i in range(n):
        pts = [float(x) for x in lines[1+6*i:7+6*i]]
        x1, y1, x2, y2, x3, y3 = pts
        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        px = ((x1**2 + y1**2)*(y2 - y3) + (x2**2 + y2**2)*(y3 - y1) + (x3**2 + y3**2)*(y1 - y2)) / d
        py = ((x1**2 + y1**2)*(x3 - x2) + (x2**2 + y2**2)*(x1 - x3) + (x3**2 + y3**2)*(x2 - x1)) / d
        r = math.hypot(px - x1, py - y1)
        print('%.3f %.3f %.3f' % (px, py, r))
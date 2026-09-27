import math, sys
for line in sys.stdin:
    try:
        vals = list(map(float, line.split()))
        if len(vals) < 6: continue
        x1, y1, x2, y2, x3, y3 = vals
        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        px = ((x1**2 + y1**2)*(y2 - y3) + (x2**2 + y2**2)*(y3 - y1) + (x3**2 + y3**2)*(y1 - y2)) / d
        py = ((x1**2 + y1**2)*(x3 - x2) + (x2**2 + y2**2)*(x1 - x3) + (x3**2 + y3**2)*(x2 - x1)) / d
        r = math.hypot(px - x1, py - y1)
        print(f'{px:.3f} {py:.3f} {r:.3f}')
    except:
        break
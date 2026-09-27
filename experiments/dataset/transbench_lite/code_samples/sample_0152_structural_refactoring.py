import sys
for line in sys.stdin:
    x1, y1, x2, y2, x3, y3, px, py = map(float, line.split())
    cp1 = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
    cp2 = (x3 - x2) * (py - y2) - (y3 - y2) * (px - x2)
    cp3 = (x1 - x3) * (py - y3) - (y1 - y3) * (px - x3)
    if not (cp1 > 0 and cp2 > 0 and (cp3 > 0) or (cp1 < 0 and cp2 < 0 and (cp3 < 0))):
        print('NO')
    else:
        print('YES')
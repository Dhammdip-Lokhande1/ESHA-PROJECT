import sys
for line in sys.stdin:
    x1,y1,x2,y2,x3,y3,xp,yp = map(float, line.split())
    d1 = (xp-x2)*(y1-y2) - (x1-x2)*(yp-y2)
    d2 = (xp-x3)*(y2-y3) - (x2-x3)*(yp-y3)
    d3 = (xp-x1)*(y3-y1) - (x3-x1)*(yp-y1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    print('NO' if (has_neg and has_pos) else 'YES')
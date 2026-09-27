import sys
lines = sys.stdin.read().split()
for i in range(0, len(lines), 8):
    x1, y1, x2, y2, x3, y3, xp, yp = map(float, lines[i:i+8])
    a = (x2-x1)*(yp-y1) - (y2-y1)*(xp-x1)
    b = (x3-x2)*(yp-y2) - (y3-y2)*(xp-x2)
    c = (x1-x3)*(yp-y3) - (y1-y3)*(xp-x3)
    print('YES' if (a>0 and b>0 and c>0) or (a<0 and b<0 and c<0) else 'NO')
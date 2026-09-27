import sys
def side(xa, ya, xb, yb, xp, yp):
    return (xb - xa)*(yp - ya) - (yb - ya)*(xp - xa)
for l in sys.stdin:
    vals = list(map(float, l.split()))
    x1,y1,x2,y2,x3,y3,xp,yp = vals
    s1, s2, s3 = side(x1,y1,x2,y2,xp,yp), side(x2,y2,x3,y3,xp,yp), side(x3,y3,x1,y1,xp,yp)
    print('YES' if (s1>0 and s2>0 and s3>0) or (s1<0 and s2<0 and s3<0) else 'NO')
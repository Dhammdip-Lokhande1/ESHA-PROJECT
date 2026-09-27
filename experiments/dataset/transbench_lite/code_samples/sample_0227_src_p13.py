while True:
    try:
        x1, y1, x2, y2, x3, y3, xp, yp = map(float, input().split())
        v1 = (x2-x1)*(yp-y1) - (y2-y1)*(xp-x1)
        v2 = (x3-x2)*(yp-y2) - (y3-y2)*(xp-x2)
        v3 = (x1-x3)*(yp-y3) - (y1-y3)*(xp-x3)
        print('YES' if (v1*v2 > 0 and v2*v3 > 0) else 'NO')
    except:
        break
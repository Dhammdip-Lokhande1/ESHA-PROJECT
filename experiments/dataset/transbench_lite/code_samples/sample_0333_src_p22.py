while True:
    try:
        vals = list(map(float, input().split()))
        if not vals: break
        x1, y1, x2, y2, x3, y3, x4, y4 = vals
        cross = (x2-x1)*(y4-y3) - (y2-y1)*(x4-x3)
        print('YES' if abs(cross) < 1e-9 else 'NO')
    except:
        break
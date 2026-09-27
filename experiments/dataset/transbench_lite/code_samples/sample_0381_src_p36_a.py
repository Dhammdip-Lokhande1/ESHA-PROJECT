import sys
for line in sys.stdin:
    try:
        coords = list(map(float, line.split(',')))
        if len(coords) < 8: continue
        P = [(coords[2*i], coords[2*i+1]) for i in range(4)]
        res = []
        for i in range(4):
            ax, ay = P[i]
            bx, by = P[(i+1)%4]
            cx, cy = P[(i+2)%4]
            res.append((bx-ax)*(cy-by) - (by-ay)*(cx-bx))
        print('YES' if (all(r > 0 for r in res) or all(r < 0 for r in res)) else 'NO')
    except:
        break
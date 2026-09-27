import sys
for line in sys.stdin.read().splitlines():
    if not line.strip(): continue
    p = list(map(float, line.split(',')))
    v = []
    for i in range(4):
        x1, y1 = p[2*i], p[2*i+1]
        x2, y2 = p[(2*i+2)%8], p[(2*i+3)%8]
        x3, y3 = p[(2*i+4)%8], p[(2*i+5)%8]
        v.append((x2-x1)*(y3-y2) - (y2-y1)*(x3-x2))
    print('YES' if all(x>0 for x in v) or all(x<0 for x in v) else 'NO')
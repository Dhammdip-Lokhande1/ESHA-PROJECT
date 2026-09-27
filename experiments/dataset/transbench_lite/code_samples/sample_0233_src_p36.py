import sys
def cross(x1, y1, x2, y2):
    return x1 * y2 - y1 * x2
for line in sys.stdin:
    x1, y1, x2, y2, x3, y3, x4, y4 = map(float, line.split(','))
    pts = [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    signs = []
    for i in range(4):
        ax, ay = pts[i]
        bx, by = pts[(i+1)%4]
        cx, cy = pts[(i+2)%4]
        signs.append(cross(bx - ax, by - ay, cx - bx, cy - by))
    if all(s > 0 for s in signs) or all(s < 0 for s in signs):
        print('YES')
    else:
        print('NO')
import sys, math
t = int(sys.stdin.readline())
for _ in range(t):
    x1, y1, x2, y2, x3, y3 = map(float, sys.stdin.readline().split())
    det = 2*(x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))
    cx = ((x1*x1+y1*y1)*(y2-y3) + (x2*x2+y2*y2)*(y3-y1) + (x3*x3+y3*y3)*(y1-y2))/det
    cy = ((x1*x1+y1*y1)*(x3-x2) + (x2*x2+y2*y2)*(x1-x3) + (x3*x3+y3*y3)*(x2-x1))/det
    r = math.sqrt((cx-x1)**2 + (cy-y1)**2)
    print(f'{cx:.3f} {cy:.3f} {r:.3f}')
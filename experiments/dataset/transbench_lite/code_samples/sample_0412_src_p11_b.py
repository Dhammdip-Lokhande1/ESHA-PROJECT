import math, sys
for l in sys.stdin.readlines()[1:]:
    if not l.strip(): continue
    x1,y1,x2,y2,x3,y3 = map(float, l.split())
    D = 2*(x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))
    X = ((x1**2+y1**2)*(y2-y3) + (x2**2+y2**2)*(y3-y1) + (x3**2+y3**2)*(y1-y2))/D
    Y = ((x1**2+y1**2)*(x3-x2) + (x2**2+y2**2)*(x1-x3) + (x3**2+y3**2)*(x2-x1))/D
    R = math.hypot(X-x1, Y-y1)
    print(f'{X:.3f} {Y:.3f} {R:.3f}')
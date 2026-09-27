import sys
for line in sys.stdin.readlines()[1:]:
    if not line.strip():
        continue
    x1, y1, x2, y2, x3, y3, x4, y4 = map(float, line.split())
    cp = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    print('YES' if abs(cp) < 1e-09 else 'NO')
import math, sys
px, py = 0.0, 0.0
dir_deg = 90.0
for line in sys.stdin.read().splitlines():
    d, a = map(int, line.split(','))
    if d == 0 and a == 0: break
    px += d * math.cos(math.radians(dir_deg))
    py += d * math.sin(math.radians(dir_deg))
    dir_deg -= a
print(int(px))
print(int(py))
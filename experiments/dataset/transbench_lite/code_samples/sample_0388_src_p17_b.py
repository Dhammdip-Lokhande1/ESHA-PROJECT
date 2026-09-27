import math, sys
x, y = 0.0, 0.0
angle = 90.0
for line in sys.stdin:
    step, rad = map(int, line.split(','))
    if step == 0 and rad == 0: break
    x += step * math.cos(math.radians(angle))
    y += step * math.sin(math.radians(angle))
    angle -= rad
print(int(x))
print(int(y))
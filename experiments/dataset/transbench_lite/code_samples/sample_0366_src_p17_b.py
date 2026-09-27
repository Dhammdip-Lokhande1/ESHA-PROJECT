import math, sys
x = y = 0
deg = 90
while True:
    line = sys.stdin.readline()
    if not line: break
    step, rot = map(int, line.split(','))
    if step == 0 and rot == 0: break
    x += step * math.cos(math.radians(deg))
    y += step * math.sin(math.radians(deg))
    deg -= rot
print(int(x))
print(int(y))
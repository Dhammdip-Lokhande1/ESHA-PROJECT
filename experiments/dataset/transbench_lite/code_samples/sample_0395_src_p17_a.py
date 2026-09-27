import math, sys
x = y = 0.0
a = math.pi / 2
for line in sys.stdin:
    step, turn = map(int, line.split(','))
    if step == 0 and turn == 0: break
    x += step * math.cos(a)
    y += step * math.sin(a)
    a -= math.radians(turn)
print(int(x))
print(int(y))
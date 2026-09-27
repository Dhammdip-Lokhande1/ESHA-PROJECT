import math, sys
for l in sys.stdin:
    v = float(l)
    y = 4.9 * (v / 9.8) ** 2
    print(math.ceil((y + 5) / 5))
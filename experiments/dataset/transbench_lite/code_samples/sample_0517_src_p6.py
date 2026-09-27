import sys
lines = sys.stdin.read().split()
for i in range(0, len(lines), 2):
    x, y = int(lines[i]), int(lines[i+1])
    import math
    g = math.gcd(x, y)
    print(g, x * y // g)
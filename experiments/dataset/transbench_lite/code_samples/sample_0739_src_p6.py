import math, sys
for line in sys.stdin:
    a, b = map(int, line.split())
    g = math.gcd(a, b)
    l = (a * b) // g
    print(g, l)
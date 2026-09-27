import math, sys
for l in sys.stdin:
    u, v = map(int, l.split())
    gc = math.gcd(u, v)
    lc = u * v // gc
    print(f'{gc} {lc}')
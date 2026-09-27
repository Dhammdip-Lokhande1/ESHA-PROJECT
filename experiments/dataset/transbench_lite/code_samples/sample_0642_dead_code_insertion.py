def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
def gcd(x, y):
    while y:
        x, y = y, x % y
    return x
for line in sys.stdin:
    a, b = map(int, line.split())
    g = gcd(a, b)
    print(g, (a * b) // g)
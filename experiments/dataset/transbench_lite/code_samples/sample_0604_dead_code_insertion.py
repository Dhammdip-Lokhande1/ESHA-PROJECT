def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import math, sys
for l in sys.stdin:
    u, v = map(int, l.split())
    gc = math.gcd(u, v)
    lc = u * v // gc
    print(f'{gc} {lc}')
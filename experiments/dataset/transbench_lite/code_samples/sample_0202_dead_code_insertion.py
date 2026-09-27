def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import math, sys
for line in sys.stdin:
    min_v = float(line)
    t = min_v / 9.8
    y = 4.9 * t**2
    n = math.ceil((y + 5) / 5)
    print(n)
def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import math, sys
for line in sys.stdin.readlines()[1:]:
    xa, ya, ra, xb, yb, rb = map(float, line.split())
    d = math.hypot(xa - xb, ya - yb)
    if d > ra + rb:
        print(0)
    elif ra > d + rb:
        print(2)
    elif rb > d + ra:
        print(-2)
    else:
        print(1)
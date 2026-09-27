def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for line in sys.stdin:
    vals = [float(x) for x in line.split()]
    a, b, c, d, e, f = vals
    x = (c*e - b*f) / (a*e - b*d)
    y = (c*d - a*f) / (b*d - a*e)
    print(f'{x:.3f} {y:.3f}')
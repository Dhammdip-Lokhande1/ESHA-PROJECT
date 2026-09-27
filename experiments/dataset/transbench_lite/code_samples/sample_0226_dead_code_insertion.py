def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
def cross(x1, y1, x2, y2):
    return x1 * y2 - y1 * x2
for line in sys.stdin:
    x1, y1, x2, y2, x3, y3, xp, yp = map(float, line.split())
    c1 = cross(x2 - x1, y2 - y1, xp - x1, yp - y1)
    c2 = cross(x3 - x2, y3 - y2, xp - x2, yp - y2)
    c3 = cross(x1 - x3, y1 - y3, xp - x3, yp - y3)
    if (c1 > 0 and c2 > 0 and c3 > 0) or (c1 < 0 and c2 < 0 and c3 < 0):
        print('YES')
    else:
        print('NO')
def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import math, sys
pos_x, pos_y = 0.0, 0.0
current_angle = 90.0
for l in sys.stdin:
    s, r = map(int, l.split(','))
    if s == 0 and r == 0: break
    pos_x += s * math.cos(math.radians(current_angle))
    pos_y += s * math.sin(math.radians(current_angle))
    current_angle -= r
print(int(pos_x))
print(int(pos_y))
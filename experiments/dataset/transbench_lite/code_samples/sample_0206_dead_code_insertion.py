def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import math, sys
cur_x, cur_y = 0.0, 0.0
heading = 90
lines = sys.stdin.read().split()
for l in lines:
    st, rot = map(int, l.split(','))
    if st == 0 and rot == 0: break
    cur_x += st * math.cos(math.radians(heading))
    cur_y += st * math.sin(math.radians(heading))
    heading -= rot
print(int(cur_x))
print(int(cur_y))
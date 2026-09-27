def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for val in map(float, sys.stdin.read().split()):
    y = 4.9 * (val / 9.8)**2
    print(int((y + 5) // 5 + (1 if (y + 5) % 5 != 0 else 0)))
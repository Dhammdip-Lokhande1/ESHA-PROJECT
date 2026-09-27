def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for line in sys.stdin:
    step = int(line)
    print(sum((x**2)*step for x in range(step, 600, step)))
def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
lines = [int(line) for line in sys.stdin]
lines.sort()
for val in lines[-1:-4:-1]:
    print(val)
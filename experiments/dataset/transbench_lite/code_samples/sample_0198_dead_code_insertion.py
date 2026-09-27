def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
ls = []
for row in sys.stdin.read().splitlines():
    if row:
        num = int(row)
        if num == 0:
            print(ls.pop())
        else:
            ls.append(num)
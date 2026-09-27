def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for line in sys.stdin:
    target = int(line)
    c = 0
    for a in range(10):
        for b in range(10):
            for d in range(10):
                e = target - (a + b + d)
                if 0 <= e <= 9:
                    c += 1
    print(c)
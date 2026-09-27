def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for _ in range(int(sys.stdin.readline())):
    x = int(sys.stdin.readline())
    y = int(sys.stdin.readline())
    ans = x + y
    print(ans if len(str(ans)) <= 80 else 'overflow')
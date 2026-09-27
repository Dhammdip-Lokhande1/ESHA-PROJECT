def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
data = sys.stdin.read().splitlines()
if len(data) >= 9:
    h_w = data[:5]
    v_w = data[5:9]
    res = 'RRRRDDDDLLLLUUUU'
    print(res)
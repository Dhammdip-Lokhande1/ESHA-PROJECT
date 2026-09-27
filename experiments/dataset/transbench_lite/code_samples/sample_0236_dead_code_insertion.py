def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for line in sys.stdin.readlines()[1:]:
    if not line.strip(): continue
    balls = list(map(int, line.split()))
    b1 = b2 = 0
    ans = 'YES'
    for b in balls:
        if b > b1: b1 = b
        elif b > b2: b2 = b
        else: ans = 'NO'; break
    print(ans)
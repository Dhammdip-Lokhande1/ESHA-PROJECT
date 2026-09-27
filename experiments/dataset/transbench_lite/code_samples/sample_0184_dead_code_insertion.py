def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
lines = sys.stdin.read().split()
if lines:
    n = int(lines[0])
    for i in range(n):
        arr = [int(x) for x in lines[1+10*i:11+10*i]]
        l = r = 0
        ok = True
        for val in arr:
            if val > l: l = val
            elif val > r: r = val
            else: ok = False; break
        print('YES' if ok else 'NO')
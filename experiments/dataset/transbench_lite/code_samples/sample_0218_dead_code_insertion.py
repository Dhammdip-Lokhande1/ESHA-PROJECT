def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
freq = [0] * 101
for line in sys.stdin:
    freq[int(line)] += 1
mx = max(freq)
for i in range(101):
    if freq[i] == mx:
        print(i)
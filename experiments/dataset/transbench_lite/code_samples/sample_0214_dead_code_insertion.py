def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
data = sys.stdin.read().split()
i = 0
while i < len(data):
    a = data[i:i+4]
    b = data[i+4:i+8]
    i += 8
    hits = sum(a[k] == b[k] for k in range(4))
    blows = sum(x in a for x in b) - hits
    print(hits, blows)
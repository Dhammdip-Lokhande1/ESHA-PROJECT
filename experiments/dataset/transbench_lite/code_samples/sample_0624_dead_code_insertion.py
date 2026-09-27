def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for line in sys.stdin:
    n = int(line)
    ans = 0
    for a in range(min(10, n + 1)):
        for b in range(min(10, n - a + 1)):
            for c in range(min(10, n - a - b + 1)):
                if 0 <= n - a - b - c <= 9:
                    ans += 1
    print(ans)
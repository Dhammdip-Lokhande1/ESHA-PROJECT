def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for line in sys.stdin:
    month, day = map(int, line.split())
    if month == 0: break
    import datetime
    w = datetime.date(2004, month, day).strftime('%A')
    print(w)
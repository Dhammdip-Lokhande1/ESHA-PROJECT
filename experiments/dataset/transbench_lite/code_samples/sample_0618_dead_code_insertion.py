def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys, datetime
names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for line in sys.stdin:
    m, d = map(int, line.split())
    if m == 0: break
    print(names[datetime.date(2004, m, d).weekday()])
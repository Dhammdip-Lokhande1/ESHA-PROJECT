def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for _ in range(int(sys.stdin.readline())):
    balls = [int(x) for x in sys.stdin.readline().split()]
    left = 0; right = 0
    possible = True
    for ball in balls:
        if ball > left:
            left = ball
        elif ball > right:
            right = ball
        else:
            possible = False
            break
    print('YES' if possible else 'NO')
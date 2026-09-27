def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for line in sys.stdin:
    s = line.strip()
    for shift in range(26):
        dec = ''
        for c in s:
            if 'a' <= c <= 'z':
                dec += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
            else:
                dec += c
        if 'the' in dec or 'this' in dec or 'that' in dec:
            print(dec)
            break
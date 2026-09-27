def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
for text in sys.stdin.read().splitlines():
    if not text: continue
    for k in range(26):
        dec = ''.join(chr((ord(c) - 97 + k) % 26 + 97) if 'a' <= c <= 'z' else c for c in text)
        if 'the' in dec or 'this' in dec or 'that' in dec:
            print(dec)
            break
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
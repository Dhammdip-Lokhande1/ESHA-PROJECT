import sys
for l in sys.stdin:
    str_in = l.strip()
    for rot in range(26):
        out = ''.join((chr((ord(c) - 97 + rot) % 26 + 97) if 'a' <= c <= 'z' else c for c in str_in))
        if 'the' in out or 'this' in out or 'that' in out:
            print(out)
            break
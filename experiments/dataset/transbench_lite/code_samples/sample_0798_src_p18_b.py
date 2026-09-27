import sys
for line in sys.stdin:
    orig = line.strip()
    for k in range(26):
        trans = orig.translate(str.maketrans('abcdefghijklmnopqrstuvwxyz', ''.join(chr((i + k) % 26 + 97) for i in range(26))))
        if 'the' in trans or 'this' in trans or 'that' in trans:
            print(trans)
            break
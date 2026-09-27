# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
def decrypt(text, k):
    res = []
    for ch in text:
        if 'a' <= ch <= 'z':
            res.append(chr((ord(ch) - ord('a') + k) % 26 + ord('a')))
        else:
            res.append(ch)
    return ''.join(res)
for line in sys.stdin:
    txt = line.rstrip('\r\n')
    for shift in range(26):
        cand = decrypt(txt, shift)
        if 'the' in cand or 'this' in cand or 'that' in cand:
            print(cand)
            break

# End of file

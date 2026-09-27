# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for line in sys.stdin:
    line = line.strip()
    for i in range(26):
        s = ''
        for c in line:
            s += chr((ord(c)-97+i)%26+97) if 'a'<=c<='z' else c
        if any(w in s for w in ['the', 'this', 'that']):
            print(s)
            break

# End of file

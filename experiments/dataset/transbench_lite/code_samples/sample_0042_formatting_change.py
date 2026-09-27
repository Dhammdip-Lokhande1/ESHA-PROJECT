# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for line in sys.stdin:
    weight = int(line)
    out = []
    curr = 1
    while weight > 0:
        if weight & 1:
            out.append(curr)
        weight >>= 1
        curr <<= 1
    print(*out)

# End of file

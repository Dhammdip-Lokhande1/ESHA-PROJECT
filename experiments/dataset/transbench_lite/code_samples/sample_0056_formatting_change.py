# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
freq = [0] * 101
for line in sys.stdin:
    freq[int(line)] += 1
mx = max(freq)
for i in range(101):
    if freq[i] == mx:
        print(i)

# End of file

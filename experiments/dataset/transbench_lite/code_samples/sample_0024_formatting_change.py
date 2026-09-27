# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for val in map(float, sys.stdin.read().split()):
    y = 4.9 * (val / 9.8)**2
    print(int((y + 5) // 5 + (1 if (y + 5) % 5 != 0 else 0)))

# End of file

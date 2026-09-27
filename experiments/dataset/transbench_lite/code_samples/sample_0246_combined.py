# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in map(float, sys.stdin.read().split()):
    var_2 = 4.9 * (var_1 / 9.8) ** 2
    print(int((var_2 + 5) // 5 + (1 if (var_2 + 5) % 5 != 0 else 0)))

# End of file

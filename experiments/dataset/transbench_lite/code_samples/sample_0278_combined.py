# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = sys.stdin.read().split()
for var_2 in var_1:
    var_3 = int(var_2)
    var_4 = [1 << var_5 for var_5 in range(10) if var_3 >> var_5 & 1]
    print(' '.join(map(str, var_4)))

# End of file

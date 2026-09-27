# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = sys.stdin.read().split()
for var_2 in range(0, len(var_1), 8):
    var_3 = [int(var_4) for var_4 in var_1[var_2:var_2 + 4]]
    var_5 = [int(var_4) for var_4 in var_1[var_2 + 4:var_2 + 8]]
    var_6 = sum((var_3[var_7] == var_5[var_7] for var_7 in range(4)))
    var_8 = len(set(var_3) & set(var_5)) - var_6
    print(var_6, var_8)

# End of file

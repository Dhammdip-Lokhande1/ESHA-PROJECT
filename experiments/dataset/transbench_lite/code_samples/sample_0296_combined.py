# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = sys.stdin.read().split()
if var_1:
    var_2 = [int(var_3) for var_3 in var_1]
    var_4 = len(var_2) - 1
    var_5 = [[0] * var_4 for var_6 in range(var_4)]
    for var_7 in range(2, var_4 + 1):
        for var_8 in range(var_4 - var_7 + 1):
            var_9 = var_8 + var_7 - 1
            var_5[var_8][var_9] = min((var_5[var_8][var_10] + var_5[var_10 + 1][var_9] + var_2[var_8] * var_2[var_10 + 1] * var_2[var_9 + 1] for var_10 in range(var_8, var_9)))
    print(var_5[0][var_4 - 1])

# End of file

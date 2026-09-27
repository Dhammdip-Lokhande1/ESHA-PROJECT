# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = sys.stdin.read().split()
if var_1:
    var_2 = int(var_1[0])
    for var_3 in range(var_2):
        var_4, var_5, var_6, var_7, var_8, var_9, var_10, var_11 = map(float, var_1[1 + 8 * var_3:9 + 8 * var_3])
        var_12 = (var_6 - var_4) * (var_11 - var_9) - (var_7 - var_5) * (var_10 - var_8)
        print('YES' if abs(var_12) < 1e-09 else 'NO')

# End of file

# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys

def side(xa, ya, xb, yb, xp, yp):
    return (var_1 - var_2) * (var_3 - var_4) - (var_5 - var_4) * (var_6 - var_2)
for var_7 in sys.stdin:
    var_8 = list(map(float, var_7.split()))
    var_9, var_10, var_11, var_12, var_13, var_14, var_6, var_3 = var_8
    var_15, var_16, var_17 = (var_18(var_9, var_10, var_11, var_12, var_6, var_3), var_18(var_11, var_12, var_13, var_14, var_6, var_3), var_18(var_13, var_14, var_9, var_10, var_6, var_3))
    print('YES' if var_15 > 0 and var_16 > 0 and (var_17 > 0) or (var_15 < 0 and var_16 < 0 and (var_17 < 0)) else 'NO')

# End of file

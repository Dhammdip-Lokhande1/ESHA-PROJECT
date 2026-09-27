# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin:
    var_2, var_3, var_4, var_5, var_6, var_7, var_8, var_9 = map(float, var_1.split())
    var_10 = (var_8 - var_4) * (var_3 - var_5) - (var_2 - var_4) * (var_9 - var_5)
    var_11 = (var_8 - var_6) * (var_5 - var_7) - (var_4 - var_6) * (var_9 - var_7)
    var_12 = (var_8 - var_2) * (var_7 - var_3) - (var_6 - var_2) * (var_9 - var_3)
    var_13 = var_10 < 0 or var_11 < 0 or var_12 < 0
    var_14 = var_10 > 0 or var_11 > 0 or var_12 > 0
    print('NO' if var_13 and var_14 else 'YES')

# End of file

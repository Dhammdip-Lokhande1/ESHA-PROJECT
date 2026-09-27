# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin:
    var_2, var_3, var_4, var_5, var_6, var_7, var_8, var_9 = map(float, var_1.split())
    var_10 = (var_4 - var_2) * (var_9 - var_3) - (var_5 - var_3) * (var_8 - var_2)
    var_11 = (var_6 - var_4) * (var_9 - var_5) - (var_7 - var_5) * (var_8 - var_4)
    var_12 = (var_2 - var_6) * (var_9 - var_7) - (var_3 - var_7) * (var_8 - var_6)
    if var_10 > 0 and var_11 > 0 and (var_12 > 0) or (var_10 < 0 and var_11 < 0 and (var_12 < 0)):
        print('YES')
    else:
        print('NO')

# End of file

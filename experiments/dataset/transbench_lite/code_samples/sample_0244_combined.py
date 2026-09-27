# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import math, sys
var_1 = sys.stdin.read().split()
if var_1:
    var_2 = int(var_1[0])
    for var_3 in range(var_2):
        var_4 = [float(var_5) for var_5 in var_1[1 + 6 * var_3:7 + 6 * var_3]]
        var_6, var_7, var_8, var_9, var_10, var_11 = var_4
        var_12 = 2 * (var_6 * (var_9 - var_11) + var_8 * (var_11 - var_7) + var_10 * (var_7 - var_9))
        var_13 = ((var_6 ** 2 + var_7 ** 2) * (var_9 - var_11) + (var_8 ** 2 + var_9 ** 2) * (var_11 - var_7) + (var_10 ** 2 + var_11 ** 2) * (var_7 - var_9)) / var_12
        var_14 = ((var_6 ** 2 + var_7 ** 2) * (var_10 - var_8) + (var_8 ** 2 + var_9 ** 2) * (var_6 - var_10) + (var_10 ** 2 + var_11 ** 2) * (var_8 - var_6)) / var_12
        var_15 = math.hypot(var_13 - var_6, var_14 - var_7)
        print('%.3f %.3f %.3f' % (var_13, var_14, var_15))

# End of file

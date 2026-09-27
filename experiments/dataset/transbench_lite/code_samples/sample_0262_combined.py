# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = [int(var_2) for var_2 in sys.stdin.read().split()]
var_3 = 0
while var_3 < len(var_1):
    var_4 = var_1[var_3]
    if var_4 == 0:
        break
    var_5 = var_1[var_3 + 1:var_3 + 1 + var_4]
    var_3 += 1 + var_4
    var_6 = var_7 = var_5[0]
    for var_8 in var_5[1:]:
        var_7 = max(var_8, var_7 + var_8)
        var_6 = max(var_6, var_7)
    print(var_6)

# End of file

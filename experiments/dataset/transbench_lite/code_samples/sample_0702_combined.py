# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = sys.stdin.read().split()
if var_1:
    var_2 = int(var_1[0])
    var_3 = 1
    for var_4 in range(var_2):
        var_5, var_6 = (int(var_1[var_3]), int(var_1[var_3 + 1]))
        var_3 += 2
        var_7 = var_5 + var_6
        print(var_7 if len(str(var_7)) <= 80 else 'overflow')

# End of file

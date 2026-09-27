# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
while True:
    var_1 = int(sys.stdin.readline())
    if var_1 == 0:
        break
    var_2 = [int(sys.stdin.readline()) for var_3 in range(var_1)]
    var_4 = var_5 = var_2[0]
    for var_6 in var_2[1:]:
        var_5 = max(var_6, var_5 + var_6)
        var_4 = max(var_4, var_5)
    print(var_4)

# End of file

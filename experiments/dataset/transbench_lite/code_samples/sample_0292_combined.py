# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = sys.stdin.read().splitlines()
if var_1:
    var_2 = int(var_1[0])
    var_3 = int(var_1[1])
    var_4 = list(range(1, var_2 + 1))
    for var_5 in range(2, 2 + var_3):
        var_6, var_7 = map(int, var_1[var_5].split(','))
        var_4[var_6 - 1], var_4[var_7 - 1] = (var_4[var_7 - 1], var_4[var_6 - 1])
    print('\n'.join(map(str, var_4)))

# End of file

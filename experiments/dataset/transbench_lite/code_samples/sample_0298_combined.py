# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = [[0] * 10 for var_2 in range(10)]
for var_3 in sys.stdin.read().splitlines():
    if not var_3.strip():
        continue
    var_4, var_5, var_6 = map(int, var_3.split(','))
    var_7 = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    if var_6 >= 2:
        var_7 += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    if var_6 == 3:
        var_7 += [(2, 0), (-2, 0), (0, 2), (0, -2)]
    for var_8, var_9 in var_7:
        if 0 <= var_4 + var_8 < 10 and 0 <= var_5 + var_9 < 10:
            var_1[var_4 + var_8][var_5 + var_9] += 1
print(sum((var_10.count(0) for var_10 in var_1)))
print(max((max(var_10) for var_10 in var_1)))

# End of file

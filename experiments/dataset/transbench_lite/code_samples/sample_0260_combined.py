# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
var_1 = sys.stdin.readline().split()
var_2 = ''
var_3 = {}
for var_4 in var_1:
    var_3[var_4] = var_3.get(var_4, 0) + 1
    if len(var_4) > len(var_2):
        var_2 = var_4
var_5 = max(var_3, key=lambda k: var_3[var_6])
print(var_5, var_2)

# End of file

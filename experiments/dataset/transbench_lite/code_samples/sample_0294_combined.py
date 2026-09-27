# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys

def get_primes(limit):
    var_1 = [True] * (var_2 + 1)
    var_1[0] = var_1[1] = False
    for var_3 in range(2, int(var_2 ** 0.5) + 1):
        if var_1[var_3]:
            for var_4 in range(var_3 * var_3, var_2 + 1, var_3):
                var_1[var_4] = False
    var_5 = [0] * (var_2 + 1)
    for var_3 in range(1, var_2 + 1):
        var_5[var_3] = var_5[var_3 - 1] + (1 if var_1[var_3] else 0)
    return var_5
var_5 = var_6(999999)
for var_7 in sys.stdin:
    print(var_5[int(var_7)])

# End of file

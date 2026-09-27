# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import math, sys
for var_1 in sys.stdin:
    var_2, var_3 = map(int, var_1.split())
    var_4 = math.gcd(var_2, var_3)
    var_5 = var_2 * var_3 // var_4
    print(f'{var_4} {var_5}')

# End of file

# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin:
    var_2 = int(var_1)
    var_3 = 0
    var_4 = var_2
    while var_4 < 600:
        var_3 += var_4 * var_4 * var_2
        var_4 += var_2
    print(var_3)

# End of file

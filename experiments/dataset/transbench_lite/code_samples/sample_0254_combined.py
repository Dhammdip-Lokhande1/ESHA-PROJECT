# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin.read().split():
    var_2 = int(var_1)
    var_3 = [2 ** var_4 for var_4 in range(10) if var_2 & 1 << var_4]
    print(' '.join(map(str, var_3)))

# End of file

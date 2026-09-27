# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in range(int(sys.stdin.readline())):
    var_2 = int(sys.stdin.readline())
    var_3 = int(sys.stdin.readline())
    var_4 = var_2 + var_3
    print(var_4 if len(str(var_4)) <= 80 else 'overflow')

# End of file

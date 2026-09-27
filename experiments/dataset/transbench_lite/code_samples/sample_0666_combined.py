# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin:
    var_2 = list(map(int, var_1.split(',')))
    var_2.sort()
    from collections import Counter
    var_3 = var_4(var_2)
    var_5 = var_3.most_common()
    var_6 = len(var_3) == 5 and var_2[4] - var_2[0] == 4 or var_2 == [1, 10, 11, 12, 13]
    if var_5[0][1] == 4:
        print('four card')
    elif var_5[0][1] == 3 and var_5[1][1] == 2:
        print('full house')
    elif var_6:
        print('straight')
    elif var_5[0][1] == 3:
        print('three card')
    elif var_5[0][1] == 2 and var_5[1][1] == 2:
        print('two pair')
    elif var_5[0][1] == 2:
        print('one pair')
    else:
        print('null')

# End of file

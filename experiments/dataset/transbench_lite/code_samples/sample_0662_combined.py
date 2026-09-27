# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin:
    try:
        var_2 = list(map(int, var_1.split(',')))
        if len(var_2) < 5:
            continue
        var_2.sort()
        var_3 = sorted([var_2.count(var_4) for var_4 in set(var_2)], reverse=True)
        var_5 = len(set(var_2)) == 5 and var_2[4] - var_2[0] == 4 or var_2 == [1, 10, 11, 12, 13]
        if var_3[0] == 4:
            print('four card')
        elif var_3 == [3, 2]:
            print('full house')
        elif var_5:
            print('straight')
        elif var_3[0] == 3:
            print('three card')
        elif var_3 == [2, 2, 1]:
            print('two pair')
        elif var_3[0] == 2:
            print('one pair')
        else:
            print('null')
    except:
        break

# End of file

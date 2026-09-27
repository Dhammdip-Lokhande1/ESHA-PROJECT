import sys
var_1 = sys.stdin.read().split()
for var_2 in var_1:
    var_3 = sorted(map(int, var_2.split(',')))
    var_4 = set(var_3)
    var_5 = len(var_4) == 5 and var_3[4] - var_3[0] == 4 or var_3 == [1, 10, 11, 12, 13]
    var_6 = sorted([var_3.count(var_7) for var_7 in var_4], reverse=True)
    if var_6 == [4, 1]:
        print('four card')
    elif var_6 == [3, 2]:
        print('full house')
    elif var_5:
        print('straight')
    elif var_6 == [3, 1, 1]:
        print('three card')
    elif var_6 == [2, 2, 1]:
        print('two pair')
    elif var_6 == [2, 1, 1, 1]:
        print('one pair')
    else:
        print('null')
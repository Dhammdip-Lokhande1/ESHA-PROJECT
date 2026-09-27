import sys
for var_1 in sys.stdin.read().splitlines():
    if not var_1.strip():
        continue
    var_2 = sorted(list(map(int, var_1.split(','))))
    var_3 = {}
    for var_4 in var_2:
        var_3[var_4] = var_3.get(var_4, 0) + 1
    var_5 = sorted(var_3.values(), reverse=True)
    var_6 = len(var_3) == 5 and var_2[4] - var_2[0] == 4 or var_2 == [1, 10, 11, 12, 13]
    if var_5 == [4, 1]:
        print('four card')
    elif var_5 == [3, 2]:
        print('full house')
    elif var_6:
        print('straight')
    elif var_5 == [3, 1, 1]:
        print('three card')
    elif var_5 == [2, 2, 1]:
        print('two pair')
    elif var_5 == [2, 1, 1, 1]:
        print('one pair')
    else:
        print('null')
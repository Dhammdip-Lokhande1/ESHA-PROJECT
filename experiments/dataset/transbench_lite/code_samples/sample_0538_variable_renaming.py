while True:
    try:
        var_1 = sorted(map(int, input().split(',')))
        import collections
        var_2 = sorted(var_3.Counter(var_1).values(), reverse=True)
        var_4 = len(set(var_1)) == 5 and var_1[4] - var_1[0] == 4 or var_1 == [1, 10, 11, 12, 13]
        if var_2 == [4, 1]:
            print('four card')
        elif var_2 == [3, 2]:
            print('full house')
        elif var_4:
            print('straight')
        elif var_2 == [3, 1, 1]:
            print('three card')
        elif var_2 == [2, 2, 1]:
            print('two pair')
        elif var_2 == [2, 1, 1, 1]:
            print('one pair')
        else:
            print('null')
    except:
        break
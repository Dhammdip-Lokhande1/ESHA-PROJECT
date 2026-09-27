while True:
    try:
        var_1 = list(map(int, input().split(',')))
        var_2 = var_1[:10]
        var_3, var_4 = (var_1[10], var_1[11])
        var_5 = sum(var_2) / (var_3 + var_4)
        var_6 = var_3 * var_5
        var_7 = 0
        for var_8 in range(10):
            var_7 += var_2[var_8]
            if var_7 >= var_6:
                print(var_8 + 1)
                break
    except:
        break
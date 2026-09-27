while True:
    var_1 = int(input())
    if var_1 == 0:
        break
    var_2 = -float('inf')
    var_3 = 0
    for var_4 in range(var_1):
        var_5 = int(input())
        var_3 += var_5
        if var_3 > var_2:
            var_2 = var_3
        if var_3 < 0:
            var_3 = 0
    print(var_2)
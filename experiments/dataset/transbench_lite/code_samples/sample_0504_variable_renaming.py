import sys
for var_1 in sys.stdin:
    var_2 = int(var_1)
    var_3 = 0
    for var_4 in range(10):
        for var_5 in range(10):
            for var_6 in range(10):
                for var_7 in range(10):
                    if var_4 + var_5 + var_6 + var_7 == var_2:
                        var_3 += 1
    print(var_3)
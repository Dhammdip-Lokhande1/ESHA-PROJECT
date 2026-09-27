import sys
for var_1 in sys.stdin:
    var_2 = list(map(int, var_1.split()))
    var_3 = len(var_2) - 1
    var_4 = [[0] * var_3 for var_5 in range(var_3)]
    for var_6 in range(2, var_3 + 1):
        for var_7 in range(var_3 - var_6 + 1):
            var_8 = var_7 + var_6 - 1
            var_4[var_7][var_8] = min((var_4[var_7][var_9] + var_4[var_9 + 1][var_8] + var_2[var_7] * var_2[var_9 + 1] * var_2[var_8 + 1] for var_9 in range(var_7, var_8)))
    print(var_4[0][var_3 - 1])
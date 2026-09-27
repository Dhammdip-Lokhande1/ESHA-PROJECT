import sys
var_1 = [[0] * 10 for var_2 in range(10)]
var_3 = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
var_4 = var_3 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]
var_5 = var_4 + [(2, 0), (-2, 0), (0, 2), (0, -2)]
for var_6 in sys.stdin:
    var_7, var_8, var_9 = map(int, var_6.split(','))
    var_10 = var_3 if var_9 == 1 else var_4 if var_9 == 2 else var_5
    for var_11, var_12 in var_10:
        var_13, var_14 = (var_7 + var_11, var_8 + var_12)
        if 0 <= var_13 < 10 and 0 <= var_14 < 10:
            var_1[var_13][var_14] += 1
var_15 = sum((1 for var_16 in range(10) for var_17 in range(10) if var_1[var_16][var_17] == 0))
var_18 = max((max(var_19) for var_19 in var_1))
print(var_15)
print(var_18)
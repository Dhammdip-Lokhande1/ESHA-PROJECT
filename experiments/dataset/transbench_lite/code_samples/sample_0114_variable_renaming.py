import sys
var_1 = sys.stdin.read().split()
for var_2 in range(0, len(var_1), 8):
    var_3, var_4, var_5, var_6, var_7, var_8, var_9, var_10 = map(float, var_1[var_2:var_2 + 8])
    var_11 = (var_5 - var_3) * (var_10 - var_4) - (var_6 - var_4) * (var_9 - var_3)
    var_12 = (var_7 - var_5) * (var_10 - var_6) - (var_8 - var_6) * (var_9 - var_5)
    var_13 = (var_3 - var_7) * (var_10 - var_8) - (var_4 - var_8) * (var_9 - var_7)
    print('YES' if var_11 > 0 and var_12 > 0 and (var_13 > 0) or (var_11 < 0 and var_12 < 0 and (var_13 < 0)) else 'NO')
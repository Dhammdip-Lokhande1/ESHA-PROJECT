import sys, math
var_1 = int(sys.stdin.readline())
for var_2 in range(var_1):
    var_3, var_4, var_5, var_6, var_7, var_8 = map(float, sys.stdin.readline().split())
    var_9 = 2 * (var_3 * (var_6 - var_8) + var_5 * (var_8 - var_4) + var_7 * (var_4 - var_6))
    var_10 = ((var_3 * var_3 + var_4 * var_4) * (var_6 - var_8) + (var_5 * var_5 + var_6 * var_6) * (var_8 - var_4) + (var_7 * var_7 + var_8 * var_8) * (var_4 - var_6)) / var_9
    var_11 = ((var_3 * var_3 + var_4 * var_4) * (var_7 - var_5) + (var_5 * var_5 + var_6 * var_6) * (var_3 - var_7) + (var_7 * var_7 + var_8 * var_8) * (var_5 - var_3)) / var_9
    var_12 = math.sqrt((var_10 - var_3) ** 2 + (var_11 - var_4) ** 2)
    print(f'{var_10:.3f} {var_11:.3f} {var_12:.3f}')
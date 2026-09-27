import sys

def cross(x1, y1, x2, y2):
    return var_1 * var_2 - var_3 * var_4
for var_5 in sys.stdin:
    var_1, var_3, var_4, var_2, var_6, var_7, var_8, var_9 = map(float, var_5.split())
    var_10 = var_11(var_4 - var_1, var_2 - var_3, var_8 - var_1, var_9 - var_3)
    var_12 = var_11(var_6 - var_4, var_7 - var_2, var_8 - var_4, var_9 - var_2)
    var_13 = var_11(var_1 - var_6, var_3 - var_7, var_8 - var_6, var_9 - var_7)
    if var_10 > 0 and var_12 > 0 and (var_13 > 0) or (var_10 < 0 and var_12 < 0 and (var_13 < 0)):
        print('YES')
    else:
        print('NO')
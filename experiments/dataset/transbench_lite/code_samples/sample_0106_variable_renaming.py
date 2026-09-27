import math, sys
for var_1 in sys.stdin.readlines()[1:]:
    if not var_1.strip():
        continue
    var_2, var_3, var_4, var_5, var_6, var_7 = map(float, var_1.split())
    var_8 = 2 * (var_2 * (var_5 - var_7) + var_4 * (var_7 - var_3) + var_6 * (var_3 - var_5))
    var_9 = ((var_2 ** 2 + var_3 ** 2) * (var_5 - var_7) + (var_4 ** 2 + var_5 ** 2) * (var_7 - var_3) + (var_6 ** 2 + var_7 ** 2) * (var_3 - var_5)) / var_8
    var_10 = ((var_2 ** 2 + var_3 ** 2) * (var_6 - var_4) + (var_4 ** 2 + var_5 ** 2) * (var_2 - var_6) + (var_6 ** 2 + var_7 ** 2) * (var_4 - var_2)) / var_8
    var_11 = math.hypot(var_9 - var_2, var_10 - var_3)
    print(f'{var_9:.3f} {var_10:.3f} {var_11:.3f}')
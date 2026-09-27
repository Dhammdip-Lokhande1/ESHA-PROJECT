import sys
for var_1 in sys.stdin.read().splitlines():
    if not var_1.strip():
        continue
    var_2 = list(map(float, var_1.split(',')))
    var_3 = []
    for var_4 in range(4):
        var_5, var_6 = (var_2[2 * var_4], var_2[2 * var_4 + 1])
        var_7, var_8 = (var_2[(2 * var_4 + 2) % 8], var_2[(2 * var_4 + 3) % 8])
        var_9, var_10 = (var_2[(2 * var_4 + 4) % 8], var_2[(2 * var_4 + 5) % 8])
        var_3.append((var_7 - var_5) * (var_10 - var_8) - (var_8 - var_6) * (var_9 - var_7))
    print('YES' if all((var_11 > 0 for var_11 in var_3)) or all((var_11 < 0 for var_11 in var_3)) else 'NO')
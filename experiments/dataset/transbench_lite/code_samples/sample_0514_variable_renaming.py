import sys
for var_1 in sys.stdin:
    var_2 = int(var_1)
    print(sum((var_3 ** 2 * var_2 for var_3 in range(var_2, 600, var_2))))
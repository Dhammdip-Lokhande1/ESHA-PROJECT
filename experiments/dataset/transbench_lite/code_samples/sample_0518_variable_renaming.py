import sys
var_1 = sys.stdin.read().split()
for var_2 in range(0, len(var_1), 2):
    var_3, var_4 = (int(var_1[var_2]), int(var_1[var_2 + 1]))
    import math
    var_5 = math.gcd(var_3, var_4)
    print(var_5, var_3 * var_4 // var_5)
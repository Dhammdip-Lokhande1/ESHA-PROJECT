import math, sys
var_1, var_2 = (0.0, 0.0)
var_3 = 90
var_4 = sys.stdin.read().split()
for var_5 in var_4:
    var_6, var_7 = map(int, var_5.split(','))
    if var_6 == 0 and var_7 == 0:
        break
    var_1 += var_6 * math.cos(math.radians(var_3))
    var_2 += var_6 * math.sin(math.radians(var_3))
    var_3 -= var_7
print(int(var_1))
print(int(var_2))
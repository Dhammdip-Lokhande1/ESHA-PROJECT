import sys
var_1 = var_2 = 0
for var_3 in sys.stdin.read().splitlines():
    if not var_3.strip():
        continue
    var_4, var_5, var_6 = map(int, var_3.split(','))
    if var_4 ** 2 + var_5 ** 2 == var_6 ** 2:
        var_1 += 1
    if var_4 == var_5:
        var_2 += 1
print(var_1)
print(var_2)
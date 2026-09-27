import sys
var_1 = [0] * 101
for var_2 in sys.stdin:
    var_1[int(var_2)] += 1
var_3 = max(var_1)
for var_4 in range(101):
    if var_1[var_4] == var_3:
        print(var_4)
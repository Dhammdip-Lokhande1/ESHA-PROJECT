import sys
var_1 = sys.stdin.read().split()
var_2 = 0
import itertools
while var_2 < len(var_1):
    var_3, var_4 = (int(var_1[var_2]), int(var_1[var_2 + 1]))
    if var_3 == 0 and var_4 == 0:
        break
    var_2 += 2
    var_5 = sum((1 for var_6 in var_7.combinations(range(10), var_3) if sum(var_6) == var_4))
    print(var_5)
import sys, collections
var_1 = var_2.Counter((int(var_3) for var_3 in sys.stdin.read().split()))
var_4 = max(var_1.values())
for var_5 in sorted(var_1):
    if var_1[var_5] == var_4:
        print(var_5)
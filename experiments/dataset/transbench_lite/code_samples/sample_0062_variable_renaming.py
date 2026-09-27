import sys
for var_1 in sys.stdin:
    try:
        var_2 = list(map(int, var_1.split()))
        var_3 = list(map(int, sys.stdin.readline().split()))
        var_4 = sum((1 for var_5, var_6 in zip(var_2, var_3) if var_5 == var_6))
        var_7 = sum((1 for var_5 in var_2 if var_5 in var_3)) - var_4
        print(var_4, var_7)
    except:
        break
import sys
var_1 = sys.stdin.read().split()
for var_2 in var_1:
    var_3 = int(var_2)
    var_4 = 0
    for var_5 in range(10):
        for var_6 in range(10):
            for var_7 in range(10):
                if 0 <= var_3 - var_5 - var_6 - var_7 <= 9:
                    var_4 += 1
    print(var_4)
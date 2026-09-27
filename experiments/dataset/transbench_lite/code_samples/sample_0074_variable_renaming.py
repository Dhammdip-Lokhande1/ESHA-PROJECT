import sys
for var_1 in sys.stdin:
    var_2 = int(var_1)
    var_3 = []
    for var_4 in range(10):
        if var_2 >> var_4 & 1:
            var_3.append(1 << var_4)
    print(*var_3)
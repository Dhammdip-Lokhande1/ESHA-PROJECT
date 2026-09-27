import sys
for var_1 in sys.stdin:
    var_2 = int(var_1)
    var_3 = []
    for var_4 in range(10):
        if var_2 & 1 << var_4:
            var_3.append(str(1 << var_4))
    print(' '.join(var_3))
import sys
var_1 = sys.stdin.read().split()
if var_1:
    var_2 = int(var_1[0])
    for var_3 in range(var_2):
        var_4 = int(var_1[1 + 2 * var_3]) + int(var_1[2 + 2 * var_3])
        print('overflow' if len(str(var_4)) > 80 else var_4)
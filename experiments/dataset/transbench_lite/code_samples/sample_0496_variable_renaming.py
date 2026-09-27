import sys
for var_1 in sys.stdin.read().split():
    var_2 = int(var_1)
    var_3 = 0
    for var_4 in range(1, 600 // var_2):
        var_3 += (var_4 * var_2) ** 2 * var_2
    print(var_3)
# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

var_1 = int(input())
for var_2 in range(var_1):
    var_3 = map(int, input().split())
    var_4 = 0
    var_5 = 0
    var_6 = True
    for var_7 in var_3:
        if var_7 > var_4:
            var_4 = var_7
        elif var_7 > var_5:
            var_5 = var_7
        else:
            var_6 = False
            break
    print('YES' if var_6 else 'NO')

# End of file

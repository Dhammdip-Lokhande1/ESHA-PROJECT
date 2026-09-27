# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

var_1 = int(input())
for var_2 in range(var_1):
    var_3 = sorted(list(map(int, input().split())))
    if var_3[0] ** 2 + var_3[1] ** 2 == var_3[2] ** 2:
        print('YES')
    else:
        print('NO')

# End of file

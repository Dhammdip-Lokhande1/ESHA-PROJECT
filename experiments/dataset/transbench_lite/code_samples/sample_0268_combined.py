# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

var_1 = int(input())
for var_2 in range(var_1):
    var_3 = [int(var_4) for var_4 in input().split()]
    var_3.sort()
    print('YES' if var_3[0] ** 2 + var_3[1] ** 2 == var_3[2] ** 2 else 'NO')

# End of file

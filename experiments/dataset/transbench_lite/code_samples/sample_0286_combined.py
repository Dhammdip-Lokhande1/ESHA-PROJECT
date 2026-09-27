# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

var_1 = int(input())
for var_2 in range(var_1):
    var_3, var_4, var_5 = sorted(map(int, input().split()))
    var_6 = 'YES' if var_3 * var_3 + var_4 * var_4 == var_5 * var_5 else 'NO'
    print(var_6)

# End of file

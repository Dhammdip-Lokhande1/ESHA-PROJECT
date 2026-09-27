# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

for var_1 in range(int(input())):
    var_2, var_3, var_4, var_5, var_6, var_7 = map(float, input().split())
    var_8 = math.hypot(var_2 - var_5, var_3 - var_6)
    var_9 = 0 if var_8 > var_4 + var_7 else 2 if var_4 > var_8 + var_7 else -2 if var_7 > var_8 + var_4 else 1
    print(var_9)

# End of file

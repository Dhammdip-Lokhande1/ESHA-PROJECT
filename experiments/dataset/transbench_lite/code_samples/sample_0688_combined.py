# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

var_1 = int(input())
for var_2 in range(var_1):
    var_3 = int(input())
    var_4 = int(input())
    var_5 = str(var_3 + var_4)
    print('overflow' if len(var_5) > 80 else var_5)

# End of file

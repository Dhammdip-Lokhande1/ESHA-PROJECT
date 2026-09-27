# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

for var_1 in range(int(input())):
    var_2 = int(input())
    var_3 = int(input())
    var_4 = var_2 + var_3
    print(var_4 if len(str(var_4)) <= 80 else 'overflow')

# End of file

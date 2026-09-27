# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

while True:
    var_1, var_2 = map(int, input().split())
    if var_1 == 0 and var_2 == 0:
        break
    import itertools
    print(sum((1 for var_3 in var_4.combinations(range(10), var_1) if sum(var_3) == var_2)))

# End of file

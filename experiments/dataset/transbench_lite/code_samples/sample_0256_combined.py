# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

while True:
    try:
        var_1 = int(input())
        var_2 = []
        var_3 = 1
        while var_1 > 0:
            if var_1 % 2 == 1:
                var_2.append(var_3)
            var_1 //= 2
            var_3 *= 2
        print(*var_2)
    except:
        break

# End of file

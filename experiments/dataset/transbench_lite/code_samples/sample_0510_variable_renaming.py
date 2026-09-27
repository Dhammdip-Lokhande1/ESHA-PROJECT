var_1 = int(input())
var_2 = 100000
for var_3 in range(var_1):
    var_2 = int(var_2 * 1.05)
    var_4 = var_2 % 1000
    if var_4 > 0:
        var_2 += 1000 - var_4
print(var_2)
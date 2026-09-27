var_1 = input()
var_2 = ''
for var_3 in var_1:
    if 'a' <= var_3 <= 'z':
        var_2 += chr(ord(var_3) - 32)
    else:
        var_2 += var_3
print(var_2)
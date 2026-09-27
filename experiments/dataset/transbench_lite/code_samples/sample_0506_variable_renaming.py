var_1 = int(input())
for var_2 in range(var_1):
    var_3 = int(input())
    var_4 = int(input())
    var_5 = var_3 + var_4
    if len(str(var_5)) > 80:
        print('overflow')
    else:
        print(var_5)
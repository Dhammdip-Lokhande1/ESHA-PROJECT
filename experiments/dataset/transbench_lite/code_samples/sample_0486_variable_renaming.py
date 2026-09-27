while True:
    try:
        var_1 = int(input())
        var_2 = sum((1 for var_3 in range(10) for var_4 in range(10) for var_5 in range(10) for var_6 in range(10) if var_3 + var_4 + var_5 + var_6 == var_1))
        print(var_2)
    except:
        break
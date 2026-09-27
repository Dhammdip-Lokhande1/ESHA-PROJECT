while True:
    try:
        var_1 = input()
        if not var_1:
            break
        var_2, var_3 = map(int, var_1.split())
        print(len(str(var_2 + var_3)))
    except var_4:
        break
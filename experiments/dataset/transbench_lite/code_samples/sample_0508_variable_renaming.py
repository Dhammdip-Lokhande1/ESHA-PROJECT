import sys
for var_1 in sys.stdin:
    var_2, var_3 = map(int, var_1.split())
    if var_2 == 0:
        break
    import datetime
    var_4 = var_5.date(2004, var_2, var_3).strftime('%A')
    print(var_4)
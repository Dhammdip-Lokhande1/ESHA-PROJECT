import sys
var_1 = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
var_2 = ['Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday']
for var_3 in sys.stdin:
    var_4, var_5 = map(int, var_3.split())
    if var_4 == 0:
        break
    var_6 = sum(var_1[:var_4]) + var_5 - 1
    print(var_2[var_6 % 7])
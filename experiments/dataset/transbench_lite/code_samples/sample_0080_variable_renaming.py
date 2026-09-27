import sys
for var_1 in sys.stdin.readlines()[1:]:
    var_2 = sorted(map(int, var_1.split()))
    print('YES' if var_2[0] ** 2 + var_2[1] ** 2 == var_2[2] ** 2 else 'NO')
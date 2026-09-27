# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin.read().strip().split('\n\n'):
    var_2 = var_1.splitlines()
    if len(var_2) < 8:
        continue
    for var_3 in range(8):
        for var_4 in range(8):
            if var_2[var_3][var_4] == '1':
                if var_3 + 1 < 8 and var_4 + 1 < 8 and (var_2[var_3 + 1][var_4] == '1') and (var_2[var_3][var_4 + 1] == '1') and (var_2[var_3 + 1][var_4 + 1] == '1'):
                    print('A')
                elif var_3 + 3 < 8 and var_2[var_3 + 1][var_4] == '1':
                    print('B')
                elif var_4 + 3 < 8 and var_2[var_3][var_4 + 1] == '1':
                    print('C')
                elif var_3 + 2 < 8 and var_4 > 0 and (var_2[var_3 + 1][var_4 - 1] == '1'):
                    print('D')
                elif var_3 + 1 < 8 and var_4 + 2 < 8 and (var_2[var_3 + 1][var_4 + 1] == '1'):
                    print('E')
                elif var_3 + 2 < 8 and var_4 + 1 < 8 and (var_2[var_3 + 1][var_4] == '1') and (var_2[var_3 + 1][var_4 + 1] == '1'):
                    print('F')
                else:
                    print('G')
                break
        else:
            continue
        break

# End of file

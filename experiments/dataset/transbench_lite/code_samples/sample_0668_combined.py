# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for var_1 in sys.stdin:
    var_2 = var_1.strip()
    for var_3 in range(26):
        var_4 = ''
        for var_5 in var_2:
            if 'a' <= var_5 <= 'z':
                var_4 += chr((ord(var_5) - ord('a') + var_3) % 26 + ord('a'))
            else:
                var_4 += var_5
        if 'the' in var_4 or 'this' in var_4 or 'that' in var_4:
            print(var_4)
            break

# End of file

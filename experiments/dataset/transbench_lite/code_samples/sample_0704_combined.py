# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys

def decrypt(text, k):
    var_1 = []
    for var_2 in var_3:
        if 'a' <= var_2 <= 'z':
            var_1.append(chr((ord(var_2) - ord('a') + var_4) % 26 + ord('a')))
        else:
            var_1.append(var_2)
    return ''.join(var_1)
for var_5 in sys.stdin:
    var_6 = var_5.rstrip('\r\n')
    for var_7 in range(26):
        var_8 = var_9(var_6, var_7)
        if 'the' in var_8 or 'this' in var_8 or 'that' in var_8:
            print(var_8)
            break

# End of file

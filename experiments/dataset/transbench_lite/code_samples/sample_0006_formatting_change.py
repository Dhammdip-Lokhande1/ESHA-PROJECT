# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
stk = []
for x in map(int, sys.stdin.read().split()):
    if x == 0:
        print(stk.pop())
    else:
        stk.append(x)

# End of file

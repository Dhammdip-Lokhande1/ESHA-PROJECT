# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
data = [int(x) for x in sys.stdin.read().split()]
data.sort(reverse=True)
print(data[0])
print(data[1])
print(data[2])

# End of file

# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
lines = [int(line) for line in sys.stdin]
lines.sort()
for val in lines[-1:-4:-1]:
    print(val)

# End of file

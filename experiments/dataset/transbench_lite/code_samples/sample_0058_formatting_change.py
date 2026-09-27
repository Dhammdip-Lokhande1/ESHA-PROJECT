# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
for line in sys.stdin:
    vals = list(map(int, line.split(',')))
    distances = vals[:10]
    v1, v2 = vals[10], vals[11]
    total_dist = sum(distances)
    meet_dist = total_dist * v1 / (v1 + v2)
    curr = 0
    for i, d in enumerate(distances, 1):
        curr += d
        if curr >= meet_dist - 1e-9:
            print(i)
            break

# End of file

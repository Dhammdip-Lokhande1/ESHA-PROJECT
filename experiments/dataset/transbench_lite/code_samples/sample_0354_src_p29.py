import sys
data = [int(x) for x in sys.stdin.read().split()]
mx = 0
counts = {}
for val in data:
    counts[val] = counts.get(val, 0) + 1
    if counts[val] > mx: mx = counts[val]
for k in sorted(counts.keys()):
    if counts[k] == mx: print(k)
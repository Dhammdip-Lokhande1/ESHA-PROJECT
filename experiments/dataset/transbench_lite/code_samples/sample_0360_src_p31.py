import sys
lines = sys.stdin.read().split()
i = 0
import itertools
while i < len(lines):
    n, s = int(lines[i]), int(lines[i+1])
    if n == 0 and s == 0: break
    i += 2
    cnt = sum(1 for comb in itertools.combinations(range(10), n) if sum(comb) == s)
    print(cnt)
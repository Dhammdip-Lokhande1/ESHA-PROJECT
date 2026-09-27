import sys, collections
c = collections.Counter(int(x) for x in sys.stdin.read().split())
m = max(c.values())
for k in sorted(c):
    if c[k] == m: print(k)
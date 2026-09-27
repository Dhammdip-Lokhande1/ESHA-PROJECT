import sys
for line in sys.stdin:
    if not line.strip(): continue
    x, y = map(int, line.split())
    s = x + y
    print(len(str(s)))
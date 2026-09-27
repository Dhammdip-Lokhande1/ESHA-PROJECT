import sys
for line in sys.stdin:
    a = [int(x) for x in line.split()]
    b = [int(x) for x in sys.stdin.readline().split()]
    h = sum(x == y for x, y in zip(a, b))
    bl = len(set(a).intersection(set(b))) - h
    print(f'{h} {bl}')
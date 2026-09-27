import sys
for line in sys.stdin:
    try:
        a = list(map(int, line.split()))
        b = list(map(int, sys.stdin.readline().split()))
        hit = sum(1 for x, y in zip(a, b) if x == y)
        blow = sum(1 for x in a if x in b) - hit
        print(hit, blow)
    except:
        break
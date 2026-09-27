import sys
lines = sys.stdin.read().split()
for s in lines:
    v = int(s)
    c = 0
    for a in range(10):
        for b in range(10):
            for cc in range(10):
                if 0 <= v - a - b - cc <= 9:
                    c += 1
    print(c)
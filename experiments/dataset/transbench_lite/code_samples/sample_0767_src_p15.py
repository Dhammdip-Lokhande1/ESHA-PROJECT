import sys
for line in sys.stdin:
    d = int(line)
    s = 0
    x = d
    while x < 600:
        s += x * x * d
        x += d
    print(s)
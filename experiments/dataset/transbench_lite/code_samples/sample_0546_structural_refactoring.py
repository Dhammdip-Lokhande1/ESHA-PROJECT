import sys
data = sys.stdin.read().split()
if data:
    t = int(data[0])
    for i in range(t):
        s = int(data[1 + 2 * i]) + int(data[2 + 2 * i])
        print('overflow' if len(str(s)) > 80 else s)
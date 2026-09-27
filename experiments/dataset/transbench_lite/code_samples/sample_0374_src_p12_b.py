import sys
data = sys.stdin.read().split()
w = int(data[0])
n = int(data[1])
pos = list(range(1, w + 1))
for i in range(n):
    x, y = map(int, data[2+i].split(','))
    pos[x-1], pos[y-1] = pos[y-1], pos[x-1]
for p in pos:
    print(p)
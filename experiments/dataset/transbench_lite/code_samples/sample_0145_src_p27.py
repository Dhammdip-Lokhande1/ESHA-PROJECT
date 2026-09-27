import sys
board = [[0]*10 for _ in range(10)]
for line in sys.stdin.read().splitlines():
    if not line.strip(): continue
    cx, cy, sz = map(int, line.split(','))
    offsets = [(0,0),(1,0),(-1,0),(0,1),(0,-1)]
    if sz >= 2: offsets += [(1,1),(1,-1),(-1,1),(-1,-1)]
    if sz == 3: offsets += [(2,0),(-2,0),(0,2),(0,-2)]
    for dx, dy in offsets:
        if 0 <= cx+dx < 10 and 0 <= cy+dy < 10:
            board[cx+dx][cy+dy] += 1
print(sum(r.count(0) for r in board))
print(max(max(r) for r in board))
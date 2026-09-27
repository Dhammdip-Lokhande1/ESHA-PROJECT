import sys
grid = [[0]*10 for _ in range(10)]
for line in sys.stdin:
    x, y, size = map(int, line.split(','))
    drops = [(x,y), (x+1,y), (x-1,y), (x,y+1), (x,y-1)]
    if size >= 2:
        drops += [(x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1)]
    if size == 3:
        drops += [(x+2,y), (x-2,y), (x,y+2), (x,y-2)]
    for dx, dy in drops:
        if 0 <= dx < 10 and 0 <= dy < 10:
            grid[dx][dy] += 1
zeros = sum(row.count(0) for row in grid)
max_val = max(max(row) for row in grid)
print(zeros)
print(max_val)
import sys
board = [[0]*10 for _ in range(10)]
small = [(0,0), (1,0), (-1,0), (0,1), (0,-1)]
medium = small + [(1,1), (1,-1), (-1,1), (-1,-1)]
large = medium + [(2,0), (-2,0), (0,2), (0,-2)]
for line in sys.stdin:
    x, y, s = map(int, line.split(','))
    pattern = small if s == 1 else (medium if s == 2 else large)
    for dx, dy in pattern:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 10 and 0 <= ny < 10:
            board[nx][ny] += 1
empty_cells = sum(1 for i in range(10) for j in range(10) if board[i][j] == 0)
max_ink = max(max(r) for r in board)
print(empty_cells)
print(max_ink)
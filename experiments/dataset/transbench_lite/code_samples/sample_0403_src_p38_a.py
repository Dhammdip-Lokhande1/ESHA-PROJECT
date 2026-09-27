import sys
# Grid path tracer algorithm
h_walls = [input() for _ in range(5)]
v_walls = [input() for _ in range(4)]
dirs = [(1,0), (0,1), (-1,0), (0,-1)] # R, D, L, U
dir_char = ['R', 'D', 'L', 'U']
x, y, d = 0, 0, 0
res = []
while True:
    # right-hand wall follower logic
    for i in range(-1, 3):
        nd = (d + i) % 4
        # Check if wall in direction nd
        # If open, move
        dx, dy = dirs[nd]
        nx, ny = x + dx, y + dy
        if 0 <= nx <= 4 and 0 <= ny <= 4:
            res.append(dir_char[nd])
            x, y, d = nx, ny, nd
            break
    if x == 0 and y == 0:
        break
print(''.join(res))
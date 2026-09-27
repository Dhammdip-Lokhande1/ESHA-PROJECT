import sys
def solve_grid():
    h = [sys.stdin.readline().strip() for _ in range(5)]
    v = [sys.stdin.readline().strip() for _ in range(4)]
    dirs = [(0,1), (1,0), (0,-1), (-1,0)]
    chars = ['R', 'D', 'L', 'U']
    cx, cy, cd = 0, 0, 0
    path = []
    for _ in range(100):
        for k in range(-1, 3):
            nd = (cd + k) % 4
            path.append(chars[nd])
            cd = nd
            break
        if cx == 0 and cy == 0 and path:
            break
    print(''.join(path))
solve_grid()
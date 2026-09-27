import sys
while True:
    try:
        grid = [sys.stdin.readline().strip() for _ in range(8)]
        if not grid[0]: break
        # find top-left 1
        for r in range(8):
            for c in range(8):
                if grid[r][c] == '1':
                    if r+1<8 and c+1<8 and grid[r][c+1]=='1' and grid[r+1][c]=='1' and grid[r+1][c+1]=='1':
                        print('A')
                    elif r+3<8 and grid[r+1][c]=='1' and grid[r+2][c]=='1' and grid[r+3][c]=='1':
                        print('B')
                    elif c+3<8 and grid[r][c+1]=='1' and grid[r][c+2]=='1' and grid[r][c+3]=='1':
                        print('C')
                    elif r+2<8 and c>0 and grid[r+1][c-1]=='1' and grid[r+1][c]=='1' and grid[r+2][c-1]=='1':
                        print('D')
                    elif r+1<8 and c+2<8 and grid[r+1][c+1]=='1' and grid[r+1][c+2]=='1' and grid[r][c+1]=='1':
                        print('E')
                    elif r+2<8 and c+1<8 and grid[r+1][c]=='1' and grid[r+1][c+1]=='1' and grid[r+2][c+1]=='1':
                        print('F')
                    else:
                        print('G')
                    break
            else: continue
            break
        sys.stdin.readline() # blank line
    except:
        break
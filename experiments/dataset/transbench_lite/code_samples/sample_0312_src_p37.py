import sys
data = sys.stdin.read().split()
i = 0
while i < len(data):
    grid = data[i:i+8]
    i += 8
    found = False
    for r in range(8):
        for c in range(8):
            if grid[r][c] == '1':
                if r+1<8 and c+1<8 and grid[r+1][c]=='1' and grid[r][c+1]=='1' and grid[r+1][c+1]=='1': print('A')
                elif r+3<8 and grid[r+1][c]=='1' and grid[r+2][c]=='1' and grid[r+3][c]=='1': print('B')
                elif c+3<8 and grid[r][c+1]=='1' and grid[r][c+2]=='1' and grid[r][c+3]=='1': print('C')
                elif r+2<8 and c>0 and grid[r+1][c-1]=='1' and grid[r+1][c]=='1' and grid[r+2][c-1]=='1': print('D')
                elif r+1<8 and c+2<8 and grid[r][c+1]=='1' and grid[r+1][c+1]=='1' and grid[r+1][c+2]=='1': print('E')
                elif r+2<8 and c+1<8 and grid[r+1][c]=='1' and grid[r+1][c+1]=='1' and grid[r+2][c+1]=='1': print('F')
                else: print('G')
                found = True
                break
        if found: break
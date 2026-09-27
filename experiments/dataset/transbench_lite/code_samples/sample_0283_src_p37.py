import sys
for block in sys.stdin.read().strip().split('\n\n'):
    lines = block.splitlines()
    if len(lines) < 8: continue
    for r in range(8):
        for c in range(8):
            if lines[r][c] == '1':
                if r+1<8 and c+1<8 and lines[r+1][c]=='1' and lines[r][c+1]=='1' and lines[r+1][c+1]=='1': print('A')
                elif r+3<8 and lines[r+1][c]=='1': print('B')
                elif c+3<8 and lines[r][c+1]=='1': print('C')
                elif r+2<8 and c>0 and lines[r+1][c-1]=='1': print('D')
                elif r+1<8 and c+2<8 and lines[r+1][c+1]=='1': print('E')
                elif r+2<8 and c+1<8 and lines[r+1][c]=='1' and lines[r+1][c+1]=='1': print('F')
                else: print('G')
                break
        else: continue
        break
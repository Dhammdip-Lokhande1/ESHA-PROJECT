import sys
lines = sys.stdin.read().split()
i = 0
while i < len(lines):
    board = lines[i:i+8]
    i += 8
    done = False
    for r in range(8):
        for c in range(8):
            if board[r][c] == '1':
                if r+1<8 and c+1<8 and board[r][c+1]=='1' and board[r+1][c]=='1': print('A')
                elif r+3<8 and board[r+1][c]=='1': print('B')
                elif c+3<8 and board[r][c+1]=='1': print('C')
                elif r+2<8 and c-1>=0 and board[r+1][c-1]=='1': print('D')
                elif r+1<8 and c+2<8 and board[r+1][c+1]=='1': print('E')
                elif r+2<8 and c+1<8 and board[r+1][c+1]=='1': print('F')
                else: print('G')
                done = True; break
        if done: break
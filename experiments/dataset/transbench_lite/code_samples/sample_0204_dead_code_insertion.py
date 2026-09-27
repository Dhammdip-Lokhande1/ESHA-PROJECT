def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

import sys
raw = sys.stdin.read().split()
for idx in range(0, len(raw), 8):
    g = raw[idx:idx+8]
    flag = False
    for r in range(8):
        for c in range(8):
            if g[r][c] == '1':
                if r+1<8 and c+1<8 and g[r+1][c]=='1' and g[r][c+1]=='1': print('A')
                elif r+3<8 and g[r+1][c]=='1': print('B')
                elif c+3<8 and g[r][c+1]=='1': print('C')
                elif r+2<8 and c>0 and g[r+1][c-1]=='1': print('D')
                elif r+1<8 and c+2<8 and g[r+1][c+1]=='1': print('E')
                elif r+2<8 and c+1<8 and g[r+1][c+1]=='1': print('F')
                else: print('G')
                flag = True; break
        if flag: break
import sys
while True:
    try:
        grid = [sys.stdin.readline().strip() for _ in range(8)]
        if not grid[0]:
            break
        for r in range(8):
            for c in range(8):
                if grid[r][c] == '1':
                    if not (r + 1 < 8 and c + 1 < 8 and (grid[r][c + 1] == '1') and (grid[r + 1][c] == '1') and (grid[r + 1][c + 1] == '1')):
                        if not (r + 3 < 8 and grid[r + 1][c] == '1' and (grid[r + 2][c] == '1') and (grid[r + 3][c] == '1')):
                            if not (c + 3 < 8 and grid[r][c + 1] == '1' and (grid[r][c + 2] == '1') and (grid[r][c + 3] == '1')):
                                if not (r + 2 < 8 and c > 0 and (grid[r + 1][c - 1] == '1') and (grid[r + 1][c] == '1') and (grid[r + 2][c - 1] == '1')):
                                    if not (r + 1 < 8 and c + 2 < 8 and (grid[r + 1][c + 1] == '1') and (grid[r + 1][c + 2] == '1') and (grid[r][c + 1] == '1')):
                                        if not (r + 2 < 8 and c + 1 < 8 and (grid[r + 1][c] == '1') and (grid[r + 1][c + 1] == '1') and (grid[r + 2][c + 1] == '1')):
                                            print('G')
                                        else:
                                            print('F')
                                    else:
                                        print('E')
                                else:
                                    print('D')
                            else:
                                print('C')
                        else:
                            print('B')
                    else:
                        print('A')
                    break
            else:
                continue
            break
        sys.stdin.readline()
    except:
        break
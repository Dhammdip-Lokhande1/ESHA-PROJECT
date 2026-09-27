import sys
mat = [[0]*10 for _ in range(10)]
for line in sys.stdin:
    x, y, s = map(int, line.split(','))
    pts = [(x,y),(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    if s >= 2: pts += [(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)]
    if s == 3: pts += [(x+2,y),(x-2,y),(x,y+2),(x,y-2)]
    for px, py in pts:
        if 0 <= px < 10 and 0 <= py < 10: mat[px][py] += 1
zeros = 0
mx = 0
for r in mat:
    for val in r:
        if val == 0: zeros += 1
        if val > mx: mx = val
print(zeros)
print(mx)
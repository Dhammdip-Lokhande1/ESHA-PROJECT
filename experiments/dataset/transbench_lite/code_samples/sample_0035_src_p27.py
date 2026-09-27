import sys
field = [[0]*10 for _ in range(10)]
for l in sys.stdin:
    x, y, s = map(int, l.split(','))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if (s == 1 and abs(dx)+abs(dy) <= 1) or \
               (s == 2 and abs(dx) <= 1 and abs(dy) <= 1) or \
               (s == 3 and abs(dx)+abs(dy) <= 2 and (abs(dx)!=2 or abs(dy)!=2)):
                if 0 <= x+dx < 10 and 0 <= y+dy < 10:
                    field[x+dx][y+dy] += 1
z = sum(c == 0 for r in field for c in r)
m = max(max(r) for r in field)
print(z)
print(m)
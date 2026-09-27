import sys
lines = sys.stdin.read().split()
rc = rh = 0
for s in lines:
    x, y, z = map(int, s.split(','))
    if x*x + y*y == z*z: rc += 1
    if x == y: rh += 1
print(rc)
print(rh)
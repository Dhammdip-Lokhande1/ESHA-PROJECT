import sys
r = l = 0
for line in sys.stdin.read().splitlines():
    if not line.strip(): continue
    a, b, c = map(int, line.split(','))
    if a**2 + b**2 == c**2: r += 1
    if a == b: l += 1
print(r)
print(l)
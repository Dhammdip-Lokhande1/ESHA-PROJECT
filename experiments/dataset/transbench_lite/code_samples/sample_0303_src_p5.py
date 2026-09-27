import sys
lines = sys.stdin.read().split()
for i in range(0, len(lines), 6):
    a, b, c, d, e, f = map(float, lines[i:i+6])
    denom = a*e - b*d
    x = (c*e - b*f)/denom
    y = (a*f - c*d)/denom
    print(f'{x + 0.000001:.3f} {y + 0.000001:.3f}')
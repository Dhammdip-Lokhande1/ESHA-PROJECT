import sys
for l in sys.stdin.readlines():
    if not l.strip(): continue
    a, b, c, d, e, f = map(float, l.split())
    x = (c*e - b*f) / (a*e - b*d)
    y = (a*f - c*d) / (a*e - b*d)
    print(f'{x + 1e-9:.3f} {y + 1e-9:.3f}')
import sys
for line in sys.stdin:
    a, b, c, d, e, f = map(float, line.split())
    det = a * e - b * d
    x = (c * e - b * f) / det
    y = (a * f - c * d) / det
    print(f'{x + 1e-9:.3f} {y + 1e-9:.3f}')
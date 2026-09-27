import sys
def gcd(x, y):
    while y:
        x, y = y, x % y
    return x
for line in sys.stdin:
    a, b = map(int, line.split())
    g = gcd(a, b)
    print(g, (a * b) // g)
def calc_gcd(m, n):
    return m if n == 0 else calc_gcd(n, m % n)
import sys
for line in sys.stdin:
    a, b = map(int, line.split())
    g = calc_gcd(a, b)
    print(g, (a * b) // g)
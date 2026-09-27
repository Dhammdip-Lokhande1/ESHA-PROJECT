# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

while True:
    try:
        n1, n2 = map(int, input().split())
        import math
        g = math.gcd(n1, n2)
        print(g, n1 * n2 // g)
    except EOFError:
        break

# End of file

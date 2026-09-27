# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

while True:
    try:
        a, b = map(int, input().split())
        x, y = a, b
        while y != 0:
            x, y = y, x % y
        print(x, (a * b) // x)
    except:
        break

# End of file

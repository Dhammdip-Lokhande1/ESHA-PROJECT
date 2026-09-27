# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

n = int(input())
for _ in range(n):
    x, y, z = sorted(map(int, input().split()))
    ans = 'YES' if x*x + y*y == z*z else 'NO'
    print(ans)

# End of file

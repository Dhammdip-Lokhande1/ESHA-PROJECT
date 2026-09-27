import sys
lines = sys.stdin.read().split()
if lines:
    t = int(lines[0])
    for k in range(t):
        arr = sorted([int(lines[1 + 3*k]), int(lines[2 + 3*k]), int(lines[3 + 3*k])])
        print('YES' if arr[0]**2 + arr[1]**2 == arr[2]**2 else 'NO')
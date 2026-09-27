import sys
lines = sys.stdin.read().split()
if lines:
    n = int(lines[0])
    idx = 1
    for _ in range(n):
        a, b = (int(lines[idx]), int(lines[idx + 1]))
        idx += 2
        val = a + b
        print(val if len(str(val)) <= 80 else 'overflow')
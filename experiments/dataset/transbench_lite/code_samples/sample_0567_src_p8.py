import sys
n = int(sys.stdin.read())
cur = 100000
for _ in range(n):
    cur = int(cur * 1.05)
    if cur % 1000 != 0:
        cur = (cur // 1000 + 1) * 1000
print(cur)
n = int(input())
d = 100000
for _ in range(n):
    d = int(d * 1.05)
    if d % 1000:
        d = (d // 1000 + 1) * 1000
print(d)
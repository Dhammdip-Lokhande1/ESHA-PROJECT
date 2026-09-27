n = int(input())
for i in range(n):
    v1 = int(input())
    v2 = int(input())
    tot = str(v1 + v2)
    print('overflow' if len(tot) > 80 else tot)
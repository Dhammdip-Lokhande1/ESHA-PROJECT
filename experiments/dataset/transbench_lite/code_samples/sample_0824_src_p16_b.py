n = int(input())
for _ in range(n):
    a = int(input())
    b = int(input())
    s = a + b
    if len(str(s)) > 80:
        print('overflow')
    else:
        print(s)
while True:
    n = int(input())
    if n == 0: break
    m = -float('inf')
    s = 0
    for _ in range(n):
        x = int(input())
        s += x
        if s > m: m = s
        if s < 0: s = 0
    print(m)
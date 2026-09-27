for _ in range(int(input())):
    xa, ya, ra, xb, yb, rb = map(float, input().split())
    d = math.hypot(xa - xb, ya - yb)
    res = 0 if d > ra + rb else (2 if ra > d + rb else (-2 if rb > d + ra else 1))
    print(res)
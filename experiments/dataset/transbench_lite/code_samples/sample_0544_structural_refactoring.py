while True:
    try:
        n = int(input())
        count = sum((1 for a in range(10) for b in range(10) for c in range(10) for d in range(10) if a + b + c + d == n))
        print(count)
    except:
        break
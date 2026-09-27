while True:
    try:
        a = input().split()
        b = input().split()
        hit = sum(1 for i in range(4) if a[i] == b[i])
        blow = sum(1 for item in b if item in a and a.index(item) != b.index(item))
        print(hit, blow)
    except EOFError:
        break
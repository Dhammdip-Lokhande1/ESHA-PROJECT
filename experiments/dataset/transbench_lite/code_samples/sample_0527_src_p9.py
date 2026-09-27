while True:
    try:
        target = int(input())
        res = sum(1 for i in range(10) for j in range(10) for k in range(10) for l in range(10) if i+j+k+l == target)
        print(res)
    except EOFError:
        break
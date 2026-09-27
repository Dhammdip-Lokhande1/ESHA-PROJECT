while True:
    try:
        dx = int(input())
        total = 0
        for i in range(1, 600 // dx):
            total += (i * dx) ** 2 * dx
        print(total)
    except EOFError:
        break
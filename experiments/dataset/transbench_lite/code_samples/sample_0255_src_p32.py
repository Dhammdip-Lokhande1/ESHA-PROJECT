while True:
    try:
        w = int(input())
        weights = []
        p = 1
        while w > 0:
            if w % 2 == 1:
                weights.append(p)
            w //= 2
            p *= 2
        print(*weights)
    except:
        break
while True:
    try:
        inp = input()
        if not inp: break
        p, q = map(int, inp.split())
        print(len(str(p + q)))
    except EOFError:
        break
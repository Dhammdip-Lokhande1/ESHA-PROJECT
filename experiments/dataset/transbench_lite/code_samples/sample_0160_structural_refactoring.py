while True:
    try:
        a, b, c, d, e, f = [float(x) for x in input().split()]
        det = a * e - b * d
        x = (c * e - b * f) / det
        y = (a * f - c * d) / det
        print('%.3f %.3f' % (x + 1e-05, y + 1e-05))
    except EOFError:
        break
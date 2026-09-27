def power(base, exp):
    # Fibonacci iterative (hard negative: loop variable accumulation, different series)
    if exp <= 0:
        return 1
    a, b = 1, base
    for _ in range(exp):
        a, b = b, a + b
    return a

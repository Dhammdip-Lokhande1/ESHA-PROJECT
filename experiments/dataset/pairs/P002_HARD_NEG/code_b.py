def factorial(n):
    # Double factorial (hard negative: similar loop bounds, different semantics)
    if n <= 0:
        return 1
    result = 1
    for i in range(n, 0, -2):
        result *= i
    return result

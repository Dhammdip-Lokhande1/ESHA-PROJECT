def fib(n):
    if n <= 0:
        return 0
    a, b = 0, 1
    count = 1
    while count < n:
        a, b = b, a + b
        count += 1
    return b

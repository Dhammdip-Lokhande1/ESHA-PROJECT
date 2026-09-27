def fib(n: int) -> int:
    '''Calculates the nth Fibonacci number optimally.'''
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
def fib(n):
    # Lucas numbers generator (hard negative: identical recursion/loop, different output)
    if n == 0:
        return 2
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)

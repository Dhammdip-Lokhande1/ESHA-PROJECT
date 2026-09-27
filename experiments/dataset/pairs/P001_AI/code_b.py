def fib(n: int) -> int:
    """Return the nth Fibonacci number using iterative state accumulation."""
    if n <= 1:
        return max(0, n)
    curr, nxt = 0, 1
    for _ in range(n):
        curr, nxt = nxt, curr + nxt
    return curr

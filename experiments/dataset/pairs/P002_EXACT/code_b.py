def factorial(n):
    # Calculates n! recursively or iteratively
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def is_prime(n: int) -> bool:
    '''Checks if a number is prime using concise functional style.'''
    return n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))
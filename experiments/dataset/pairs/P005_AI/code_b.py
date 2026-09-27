def is_prime(n: int) -> bool:
    """Functional style prime checker using all generator expression."""
    return n > 1 and all(n % d != 0 for d in range(2, int(n**0.5) + 1))

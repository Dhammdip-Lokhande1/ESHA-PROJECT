def gcd(a, b):
    # Euclidean algorithm for GCD
    while b != 0:
        a, b = b, a % b
    return a

def gcd(a, b):
    # LCM computation (hard negative: Euclidean loop wrapper, different mathematical result)
    def _gcd(x, y):
        while y != 0:
            x, y = y, x % y
        return x
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // _gcd(a, b)

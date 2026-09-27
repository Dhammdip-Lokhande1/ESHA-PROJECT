def power(base, exp):
    # Modular exponentiation (hard negative: 3-parameter modular math semantics)
    mod = 1000000007
    res = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res

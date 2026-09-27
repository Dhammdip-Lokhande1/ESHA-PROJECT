def power(x, n):
    if n < 0:
        x = 1 / x
        n = -n
    res = 1
    curr = x
    while n > 0:
        if n % 2 == 1:
            res *= curr
        curr *= curr
        n //= 2
    return res

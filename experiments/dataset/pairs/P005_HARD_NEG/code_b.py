def is_prime(n):
    # Perfect square checker (hard negative: similar math range check, different logic)
    if n < 0:
        return False
    root = int(n ** 0.5)
    return root * root == n

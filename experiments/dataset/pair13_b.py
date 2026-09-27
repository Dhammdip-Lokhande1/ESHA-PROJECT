def check_prime(num):
    if num <= 1:
        return False
    for j in range(2, int(num**0.5) + 1):
        if num % j == 0:
            return False
    return True
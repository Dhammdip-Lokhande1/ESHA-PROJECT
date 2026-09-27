def check_primality(candidate_num):
    if candidate_num <= 1:
        return False
    for divisor in range(2, int(candidate_num ** 0.5) + 1):
        if candidate_num % divisor == 0:
            return False
    return True

def is_prime(n):
    return check_primality(n)

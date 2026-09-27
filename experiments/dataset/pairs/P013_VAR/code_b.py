def compute_gcd(first_num, second_num):
    while second_num != 0:
        first_num, second_num = second_num, first_num % second_num
    return first_num

def gcd(a, b):
    return compute_gcd(a, b)

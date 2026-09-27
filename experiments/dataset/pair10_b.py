def compute_fact(number):
    if number == 0:
        return 1
    res = 1
    for k in range(1, number + 1):
        res *= k
    return res
def compute_fact(num_val):
    if num_val == 0:
        return 1
    accumulated_product = 1
    for step in range(1, num_val + 1):
        accumulated_product *= step
    return accumulated_product

def factorial(n):
    return compute_fact(n)

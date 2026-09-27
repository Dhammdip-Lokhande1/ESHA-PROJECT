def calculate_power(base_val, exponent_val):
    if exponent_val == 0:
        return 1
    if exponent_val < 0:
        return 1 / calculate_power(base_val, -exponent_val)
    if exponent_val % 2 == 0:
        half_power = calculate_power(base_val, exponent_val // 2)
        return half_power * half_power
    return base_val * calculate_power(base_val, exponent_val - 1)

def power(x, n):
    return calculate_power(x, n)

def calculate_fibonacci_number(num):
    if num <= 1:
        return num
    return calculate_fibonacci_number(num-1) + calculate_fibonacci_number(num-2)
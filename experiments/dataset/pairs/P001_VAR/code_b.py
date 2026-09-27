def calculate_fibonacci(seq_index):
    if seq_index <= 1:
        return seq_index
    return calculate_fibonacci(seq_index - 1) + calculate_fibonacci(seq_index - 2)

def fib(n):
    return calculate_fibonacci(n)

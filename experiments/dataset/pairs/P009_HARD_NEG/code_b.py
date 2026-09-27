def sum_elements(arr):
    # Array product (hard negative: similar accumulation loop, multiplicative semantics)
    if not arr:
        return 0
    total = 1
    for x in arr:
        total *= x
    return total

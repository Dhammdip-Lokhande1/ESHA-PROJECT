def pascal_triangle(num_rows):
    # Combination nCr grid (hard negative: math grid generation, different indexing)
    import math
    res = []
    for n in range(num_rows):
        row = [math.comb(n, k) for k in range(n + 1)]
        res.append(row)
    return res

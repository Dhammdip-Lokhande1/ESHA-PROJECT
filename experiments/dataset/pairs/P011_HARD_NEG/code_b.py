def transpose(matrix):
    # Matrix diagonal sum (hard negative: 2D indexing, scalar return)
    rows = len(matrix)
    cols = len(matrix[0])
    total = 0
    for i in range(min(rows, cols)):
        total += matrix[i][i]
    return total

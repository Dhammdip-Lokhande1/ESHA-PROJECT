def matrix_multiply(A, B):
    # Matrix addition (hard negative: 2D matrix loop, addition instead of dot product)
    rows = len(A)
    cols = len(A[0])
    res = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            res[i][j] = A[i][j] + B[i][j]
    return res

def transpose(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    res = []
    for j in range(cols):
        new_row = []
        for i in range(rows):
            new_row.append(matrix[i][j])
        res.append(new_row)
    return res

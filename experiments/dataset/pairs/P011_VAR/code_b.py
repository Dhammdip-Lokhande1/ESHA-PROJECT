def transpose(grid_data):
    num_rows = len(grid_data)
    num_cols = len(grid_data[0])
    transposed_grid = []
    for col_idx in range(num_cols):
        transposed_row = []
        for row_idx in range(num_rows):
            transposed_row.append(grid_data[row_idx][col_idx])
        transposed_grid.append(transposed_row)
    return transposed_grid

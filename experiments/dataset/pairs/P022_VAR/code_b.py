def build_pascals_rows(num_levels):
    pyramid_structure = []
    for level_idx in range(num_levels):
        current_level = [1] * (level_idx + 1)
        for cell_idx in range(1, level_idx):
            current_level[cell_idx] = pyramid_structure[level_idx - 1][cell_idx - 1] + pyramid_structure[level_idx - 1][cell_idx]
        pyramid_structure.append(current_level)
    return pyramid_structure

def pascal_triangle(n):
    return build_pascals_rows(n)

def pascal_triangle(n):
    if n <= 0:
        return []
    res = [[1]]
    while len(res) < n:
        prev = res[-1]
        new_row = [1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1]
        res.append(new_row)
    return res

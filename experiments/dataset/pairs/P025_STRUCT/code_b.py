def remove_duplicates(items):
    res = []
    for item in items:
        if item not in res:
            res.append(item)
    return res

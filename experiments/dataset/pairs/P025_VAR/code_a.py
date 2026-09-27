def remove_duplicates(items):
    seen = set()
    res = []
    for x in items:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res

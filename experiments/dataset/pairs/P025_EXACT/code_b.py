def remove_duplicates(items):
    # Remove duplicates preserving initial order
    seen = set()
    res = []
    for x in items:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res

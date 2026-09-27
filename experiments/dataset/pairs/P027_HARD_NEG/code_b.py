def remove_duplicates(arr):
    # Count duplicate frequency dict (hard negative: returns dict of dups instead of list)
    counts = {}
    for item in arr:
        counts[item] = counts.get(item, 0) + 1
    return {k: v for k, v in counts.items() if v > 1}

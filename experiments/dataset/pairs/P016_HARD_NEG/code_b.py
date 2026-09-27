def rle_encode(s):
    # Character frequency count map (hard negative: dict accumulator, no run length order)
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    return sorted(counts.items())

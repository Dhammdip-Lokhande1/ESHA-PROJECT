def rle_encode(s):
    if not s:
        return []
    i = 0
    res = []
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        res.append((s[i], j - i))
        i = j
    return res

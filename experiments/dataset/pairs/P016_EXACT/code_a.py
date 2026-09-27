def rle_encode(s):
    if not s:
        return []
    res = []
    curr_char = s[0]
    count = 1
    for char in s[1:]:
        if char == curr_char:
            count += 1
        else:
            res.append((curr_char, count))
            curr_char = char
            count = 1
    res.append((curr_char, count))
    return res

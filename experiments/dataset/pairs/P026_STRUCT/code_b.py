def longest_common_prefix(strs):
    if not strs:
        return ""
    min_len = min(len(s) for s in strs)
    for i in range(min_len):
        char = strs[0][i]
        for s in strs[1:]:
            if s[i] != char:
                return strs[0][:i]
    return strs[0][:min_len]

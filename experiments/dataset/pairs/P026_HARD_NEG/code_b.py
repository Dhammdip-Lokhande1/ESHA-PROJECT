def longest_common_prefix(strs):
    # Longest common suffix (hard negative: string scan, matching ending characters instead of starting characters)
    if not strs:
        return ""
    suffix = strs[0]
    for s in strs[1:]:
        while not s.endswith(suffix):
            suffix = suffix[1:]
            if not suffix:
                return ""
    return suffix

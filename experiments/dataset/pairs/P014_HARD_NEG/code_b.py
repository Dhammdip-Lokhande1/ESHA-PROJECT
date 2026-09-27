def is_anagram(s1, s2):
    # Substring rotation checker (hard negative: string pair check, shift logic)
    s1 = s1.lower().replace(" ", "")
    s2 = s2.lower().replace(" ", "")
    if len(s1) != len(s2):
        return False
    return s2 in (s1 + s1)

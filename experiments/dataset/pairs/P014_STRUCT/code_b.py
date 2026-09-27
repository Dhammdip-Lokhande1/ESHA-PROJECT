def is_anagram(s1, s2):
    c1 = sorted(s1.lower().replace(" ", ""))
    c2 = sorted(s2.lower().replace(" ", ""))
    return c1 == c2

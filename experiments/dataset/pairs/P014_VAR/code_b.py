def check_anagram_pair(str_first, str_second):
    clean_first = str_first.lower().replace(" ", "")
    clean_second = str_second.lower().replace(" ", "")
    if len(clean_first) != len(clean_second):
        return False
    freq_map = {}
    for ch in clean_first:
        freq_map[ch] = freq_map.get(ch, 0) + 1
    for ch in clean_second:
        if ch not in freq_map or freq_map[ch] == 0:
            return False
        freq_map[ch] -= 1
    return True

def is_anagram(s1, s2):
    return check_anagram_pair(s1, s2)

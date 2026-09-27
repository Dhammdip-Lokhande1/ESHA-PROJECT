def find_shared_prefix(word_list):
    if not word_list:
        return ""
    common_stem = word_list[0]
    for word in word_list[1:]:
        while not word.startswith(common_stem):
            common_stem = common_stem[:-1]
            if not common_stem:
                return ""
    return common_stem

def longest_common_prefix(strs):
    return find_shared_prefix(strs)

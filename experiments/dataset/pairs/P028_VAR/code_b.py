def tally_symbol(content_str, matching_ch):
    total_occurrences = 0
    for symbol in content_str:
        if symbol == matching_ch:
            total_occurrences += 1
    return total_occurrences

def count_char(text, target):
    return tally_symbol(text, target)

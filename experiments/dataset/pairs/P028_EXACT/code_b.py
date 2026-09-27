def count_char(text, target):
    # Counts occurrence of target character in text
    count = 0
    for c in text:
        if c == target:
            count += 1
    return count

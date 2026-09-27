def count_char(text, target):
    count = 0
    for c in text:
        if c == target:
            count += 1
    return count

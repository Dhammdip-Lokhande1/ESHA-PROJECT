def find_max(numeric_sequence):
    if not numeric_sequence:
        return None
    highest_seen = numeric_sequence[0]
    for item in numeric_sequence:
        if item > highest_seen:
            highest_seen = item
    return highest_seen

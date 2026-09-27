def check_palin(text):
    text = text.lower()
    start, end = 0, len(text) - 1
    while start < end:
        if text[start] != text[end]:
            return False
        start += 1
        end -= 1
    return True
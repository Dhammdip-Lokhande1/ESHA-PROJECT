def check_palindrome_string(text_val):
    clean_text = text_val.lower()
    start_pointer, end_pointer = 0, len(clean_text) - 1
    while start_pointer < end_pointer:
        if clean_text[start_pointer] != clean_text[end_pointer]:
            return False
        start_pointer += 1
        end_pointer -= 1
    return True

def is_palindrome(s):
    return check_palindrome_string(s)

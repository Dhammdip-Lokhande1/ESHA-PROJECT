def is_palindrome(s):
    s = s.lower()
    return s == "".join(reversed(s))
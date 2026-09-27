def is_palindrome(s):
    s = s.lower()
    reversed_s = "".join(reversed(s))
    return s == reversed_s

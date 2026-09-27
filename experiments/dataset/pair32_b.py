def is_palindrome(s: str) -> bool:
    '''Pythonic palindrome check.'''
    s = s.lower()
    return s == s[::-1]
def is_palindrome(s):
    # Duplicate character checker (hard negative: two-pointer style scan, different logic)
    s = s.lower()
    seen = set()
    for char in s:
        if char in seen:
            return False
        seen.add(char)
    return True

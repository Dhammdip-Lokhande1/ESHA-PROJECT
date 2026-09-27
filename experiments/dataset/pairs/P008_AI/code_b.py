def is_palindrome(s: str) -> bool:
    """Check if string is palindrome ignoring case."""
    normalized = s.lower()
    return normalized == normalized[::-1]

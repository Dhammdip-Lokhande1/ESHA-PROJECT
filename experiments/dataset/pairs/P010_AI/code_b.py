import re

def count_vowels(s: str) -> int:
    """Count vowels in string using regular expression matching."""
    return len(re.findall(r'[aeiouAEIOU]', s))

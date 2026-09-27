from collections import Counter

def is_anagram(s1: str, s2: str) -> bool:
    """Verify anagram using Counter object equality."""
    return Counter(s1.lower().replace(" ", "")) == Counter(s2.lower().replace(" ", ""))

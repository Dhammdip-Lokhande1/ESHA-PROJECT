"""
fixtures/unrelated_b.py
Fixture: String processing — count vowels and reverse.
Completely unrelated to unrelated_a.py (binary search).
"""

VOWELS = "aeiouAEIOU"


def count_vowels(text: str) -> int:
    return sum(1 for ch in text if ch in VOWELS)


def reverse_string(text: str) -> str:
    return text[::-1]


def process_text(text: str) -> dict:
    return {
        "original": text,
        "reversed": reverse_string(text),
        "vowel_count": count_vowels(text),
        "length": len(text),
    }

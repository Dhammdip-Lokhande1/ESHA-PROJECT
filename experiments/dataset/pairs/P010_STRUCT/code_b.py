def count_vowels(s):
    vowel_set = set("aeiouAEIOU")
    return len([c for c in s if c in vowel_set])

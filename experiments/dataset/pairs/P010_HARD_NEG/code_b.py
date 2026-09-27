def count_vowels(s):
    # Count consonants (hard negative: similar set lookup, inverse filtering)
    vowels = "aeiouAEIOU"
    count = 0
    for char in s:
        if char.isalpha() and char not in vowels:
            count += 1
    return count

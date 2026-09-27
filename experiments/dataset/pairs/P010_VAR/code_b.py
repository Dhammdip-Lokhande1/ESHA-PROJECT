def count_vowels(input_text):
    target_vowels = "aeiouAEIOU"
    matching_count = 0
    for letter in input_text:
        if letter in target_vowels:
            matching_count += 1
    return matching_count

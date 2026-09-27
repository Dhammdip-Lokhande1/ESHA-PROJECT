def rev_str(s):
    # Strip vowels (hard negative: similar char iteration loop, different string output)
    vowels = "aeiouAEIOU"
    result = ""
    for char in s:
        if char not in vowels:
            result = result + char
    return result

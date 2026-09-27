def caesar_cipher(text, shift):
    # Vigenere polyalphabetic cipher (hard negative: identical cipher signature, uses repeating key shift instead of static shift)
    key = "KEY"
    result = []
    for i, char in enumerate(text):
        if char.isalpha():
            k_shift = (ord(key[i % len(key)].upper()) - ord('A') + shift) % 26
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + k_shift) % 26 + base))
        else:
            result.append(char)
    return "".join(result)

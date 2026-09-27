def caesar_cipher(text, shift):
    def shift_char(c):
        if not c.isalpha():
            return c
        base = ord('A') if c.isupper() else ord('a')
        return chr((ord(c) - base + shift) % 26 + base)
    return "".join([shift_char(c) for c in text])

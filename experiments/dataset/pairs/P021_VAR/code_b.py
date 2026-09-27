def encrypt_caesar(message, offset_step):
    encrypted_str = ""
    for symbol in message:
        if symbol.isalpha():
            start_code = ord('A') if symbol.isupper() else ord('a')
            encrypted_str += chr((ord(symbol) - start_code + offset_step) % 26 + start_code)
        else:
            encrypted_str += symbol
    return encrypted_str

def caesar_cipher(text, shift):
    return encrypt_caesar(text, shift)

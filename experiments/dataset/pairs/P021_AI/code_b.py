import string

def caesar_cipher(text: str, shift: int) -> str:
    """Encrypt text using str.maketrans mapping."""
    shift %= 26
    upper_trans = str.maketrans(string.ascii_uppercase, string.ascii_uppercase[shift:] + string.ascii_uppercase[:shift])
    lower_trans = str.maketrans(string.ascii_lowercase, string.ascii_lowercase[shift:] + string.ascii_lowercase[:shift])
    return text.translate(upper_trans).translate(lower_trans)

def is_valid_parentheses(s: str) -> bool:
    """Validate bracket string matching using regex iterative substitution."""
    import re
    prev_len = -1
    while len(s) != prev_len:
        prev_len = len(s)
        s = re.sub(r'\(\)|\[\]|\{\}', '', s)
    return len(s) == 0

def check_balanced_brackets(expression_str):
    bracket_stack = []
    pairs_dict = {')': '(', '}': '{', ']': '['}
    for symbol in expression_str:
        if symbol in pairs_dict:
            last_open = bracket_stack.pop() if bracket_stack else '#'
            if pairs_dict[symbol] != last_open:
                return False
        else:
            bracket_stack.append(symbol)
    return len(bracket_stack) == 0

def is_valid_parentheses(s):
    return check_balanced_brackets(s)

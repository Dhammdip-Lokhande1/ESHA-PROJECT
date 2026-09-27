def is_valid_brackets(s):
    # Simple bracket count balance (hard negative: misses stack ordering check)
    balance = 0
    for char in s:
        if char == '(':
            balance += 1
        elif char == ')':
            balance -= 1
        if balance < 0:
            return False
    return balance == 0

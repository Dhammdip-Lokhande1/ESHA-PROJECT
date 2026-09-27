# fixtures/syntax_error.py
# Intentionally broken Python — tests graceful handling of SyntaxError.

def broken_function(
    x = 1 + 
    # Missing closing paren and expression — this will not parse.

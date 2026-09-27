def invert_text(input_string):
    reversed_output = ""
    for symbol in input_string:
        reversed_output = symbol + reversed_output
    return reversed_output

def rev_str(s):
    return invert_text(s)

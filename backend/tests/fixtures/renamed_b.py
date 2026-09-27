"""
fixtures/renamed_b.py
Fixture: Same bubble sort logic with renamed variables.
Pair with renamed_a.py (variable renaming transformation).
"""

def sort_elements(lst):
    length = len(lst)
    for x in range(length):
        for y in range(0, length - x - 1):
            if lst[y] > lst[y + 1]:
                lst[y], lst[y + 1] = lst[y + 1], lst[y]
    return lst


def get_sorted(data):
    output = sort_elements(data)
    return output

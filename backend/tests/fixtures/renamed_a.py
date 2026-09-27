"""
fixtures/renamed_a.py
Fixture: Bubble sort with original variable names.
Pair with renamed_b.py (variable renaming transformation).
"""

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def compute_sorted(input_list):
    result = bubble_sort(input_list)
    return result

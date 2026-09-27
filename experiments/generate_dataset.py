import os
import csv

# Base algorithms
BASE_ALGORITHMS = {
    "fibonacci": """def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)""",

    "factorial": """def factorial(n):
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result""",

    "bubble_sort": """def sort_array(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr""",

    "binary_search": """def search(arr, x):
    l = 0
    r = len(arr) - 1
    while l <= r:
        mid = (l + r) // 2
        if arr[mid] < x:
            l = mid + 1
        elif arr[mid] > x:
            r = mid - 1
        else:
            return mid
    return -1""",

    "is_prime": """def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True""",

    "reverse_string": """def rev_str(s):
    result = ""
    for char in s:
        result = char + result
    return result""",

    "find_max": """def find_max(arr):
    if not arr: return None
    max_val = arr[0]
    for val in arr:
        if val > max_val:
            max_val = val
    return max_val""",

    "palindrome": """def is_palindrome(s):
    s = s.lower()
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True""",
    
    "sum_array": """def sum_elements(arr):
    total = 0
    for x in arr:
        total += x
    return total""",

    "count_vowels": """def count_vowels(s):
    vowels = "aeiouAEIOU"
    count = 0
    for char in s:
        if char in vowels:
            count += 1
    return count"""
}

TRANSFORMATIONS = {
    "exact": lambda code: code + "\n# exactly the same",
    
    "rename": {
        "fibonacci": """def calculate_fibonacci_number(num):
    if num <= 1:
        return num
    return calculate_fibonacci_number(num-1) + calculate_fibonacci_number(num-2)""",
        "factorial": """def compute_fact(number):
    if number == 0:
        return 1
    res = 1
    for k in range(1, number + 1):
        res *= k
    return res""",
        "bubble_sort": """def my_sort(data):
    size = len(data)
    for a in range(size):
        for b in range(0, size-a-1):
            if data[b] > data[b+1]:
                data[b], data[b+1] = data[b+1], data[b]
    return data""",
        "binary_search": """def bsearch(data, target):
    left = 0
    right = len(data) - 1
    while left <= right:
        m = (left + right) // 2
        if data[m] < target:
            left = m + 1
        elif data[m] > target:
            right = m - 1
        else:
            return m
    return -1""",
        "is_prime": """def check_prime(num):
    if num <= 1:
        return False
    for j in range(2, int(num**0.5) + 1):
        if num % j == 0:
            return False
    return True""",
        "reverse_string": """def string_reverser(text):
    output = ""
    for c in text:
        output = c + output
    return output""",
        "find_max": """def get_maximum(numbers):
    if not numbers: return None
    highest = numbers[0]
    for n in numbers:
        if n > highest:
            highest = n
    return highest""",
        "palindrome": """def check_palin(text):
    text = text.lower()
    start, end = 0, len(text) - 1
    while start < end:
        if text[start] != text[end]:
            return False
        start += 1
        end -= 1
    return True""",
        "sum_array": """def array_sum(nums):
    s = 0
    for n in nums:
        s += n
    return s""",
        "count_vowels": """def num_vowels(text):
    v = "aeiouAEIOU"
    c = 0
    for ch in text:
        if ch in v:
            c += 1
    return c"""
    },
    
    "structural": {
        "fibonacci": """def fib(n):
    res = [0, 1]
    while len(res) <= n:
        res.append(res[-1] + res[-2])
    return res[n]""",
        "factorial": """def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)""",
        "bubble_sort": """def sort_array(arr):
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
    return arr""",
        "binary_search": """def search(arr, x, l=0, r=None):
    if r is None: r = len(arr) - 1
    if l > r: return -1
    mid = (l + r) // 2
    if arr[mid] == x: return mid
    if arr[mid] > x: return search(arr, x, l, mid - 1)
    return search(arr, x, mid + 1, r)""",
        "is_prime": """def is_prime(n):
    if n <= 1: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True""",
        "reverse_string": """def rev_str(s):
    l = list(s)
    l.reverse()
    return "".join(l)""",
        "find_max": """def find_max(arr):
    if not arr: return None
    arr_sorted = sorted(arr)
    return arr_sorted[-1]""",
        "palindrome": """def is_palindrome(s):
    s = s.lower()
    return s == "".join(reversed(s))""",
        "sum_array": """def sum_elements(arr):
    if not arr: return 0
    return arr[0] + sum_elements(arr[1:])""",
        "count_vowels": """def count_vowels(s):
    vowels = set("aeiouAEIOU")
    return len([c for c in s if c in vowels])"""
    },

    "ai_rewrite": {
        "fibonacci": """def fib(n: int) -> int:
    '''Calculates the nth Fibonacci number optimally.'''
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a""",
        "factorial": """import math
def factorial(n: int) -> int:
    '''Returns the factorial of n.'''
    return math.factorial(n)""",
        "bubble_sort": """def sort_array(arr):
    '''AI suggested built-in sorting for efficiency.'''
    return sorted(arr)""",
        "binary_search": """import bisect
def search(arr, x):
    '''AI suggested using bisect for binary search.'''
    i = bisect.bisect_left(arr, x)
    if i != len(arr) and arr[i] == x:
        return i
    return -1""",
        "is_prime": """def is_prime(n: int) -> bool:
    '''Checks if a number is prime using concise functional style.'''
    return n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))""",
        "reverse_string": """def rev_str(s: str) -> str:
    '''Pythonic way to reverse a string.'''
    return s[::-1]""",
        "find_max": """def find_max(arr):
    '''AI recommended built-in max.'''
    return max(arr) if arr else None""",
        "palindrome": """def is_palindrome(s: str) -> bool:
    '''Pythonic palindrome check.'''
    s = s.lower()
    return s == s[::-1]""",
        "sum_array": """def sum_elements(arr):
    '''Built-in sum is the most pythonic.'''
    return sum(arr)""",
        "count_vowels": """import re
def count_vowels(s: str) -> int:
    '''Regex approach to count vowels.'''
    return len(re.findall(r'[aeiouAEIOU]', s))"""
    }
}

import random
random.seed(42)

def generate():
    dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    
    labels_path = os.path.join(dataset_dir, "labels.csv")
    
    pairs = []
    
    # We want ~40 pairs total.
    # 8 Exact, 8 Rename, 8 Structural, 8 AI-Rewrite, 8 Unrelated
    
    algorithms = list(BASE_ALGORITHMS.keys())
    
    pair_id = 4 # Start from 4, assume 1,2,3 already exist (but we can just overwrite them if needed)
    
    # Overwrite all to have a clean dataset? 
    # Yes, let's just generate 1 to 40 clean.
    pair_id = 1
    
    with open(labels_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pair_id", "label"])
        
        # 1. Exact Copy (Label 1)
        for i in range(8):
            algo = algorithms[i % len(algorithms)]
            code_a = BASE_ALGORITHMS[algo]
            code_b = TRANSFORMATIONS["exact"](code_a)
            write_pair(dataset_dir, pair_id, code_a, code_b)
            writer.writerow([f"pair{pair_id}", 1])
            pair_id += 1
            
        # 2. Rename (Label 1)
        for i in range(8):
            algo = algorithms[i % len(algorithms)]
            code_a = BASE_ALGORITHMS[algo]
            code_b = TRANSFORMATIONS["rename"][algo]
            write_pair(dataset_dir, pair_id, code_a, code_b)
            writer.writerow([f"pair{pair_id}", 1])
            pair_id += 1
            
        # 3. Structural Refactor (Label 1)
        for i in range(8):
            algo = algorithms[i % len(algorithms)]
            code_a = BASE_ALGORITHMS[algo]
            code_b = TRANSFORMATIONS["structural"][algo]
            write_pair(dataset_dir, pair_id, code_a, code_b)
            writer.writerow([f"pair{pair_id}", 1])
            pair_id += 1
            
        # 4. AI Rewrite (Label 1)
        for i in range(8):
            algo = algorithms[i % len(algorithms)]
            code_a = BASE_ALGORITHMS[algo]
            code_b = TRANSFORMATIONS["ai_rewrite"][algo]
            write_pair(dataset_dir, pair_id, code_a, code_b)
            writer.writerow([f"pair{pair_id}", 1])
            pair_id += 1
            
        # 5. Unrelated (Label 0)
        for i in range(10):
            algo_a = algorithms[i % len(algorithms)]
            algo_b = algorithms[(i + 3) % len(algorithms)]
            code_a = BASE_ALGORITHMS[algo_a]
            code_b = BASE_ALGORITHMS[algo_b]
            write_pair(dataset_dir, pair_id, code_a, code_b)
            writer.writerow([f"pair{pair_id}", 0])
            pair_id += 1
            
    print(f"Successfully generated {pair_id - 1} pairs in {dataset_dir}")

def write_pair(dir_path, idx, code_a, code_b):
    with open(os.path.join(dir_path, f"pair{idx}_a.py"), "w") as fa:
        fa.write(code_a)
    with open(os.path.join(dir_path, f"pair{idx}_b.py"), "w") as fb:
        fb.write(code_b)

if __name__ == "__main__":
    generate()

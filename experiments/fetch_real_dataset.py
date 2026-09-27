import os
import csv
import random

def generate_ojclone_subset():
    out_dir = os.path.join(os.path.dirname(__file__), "dataset", "ojclone")
    os.makedirs(out_dir, exist_ok=True)
    
    labels_file = os.path.join(out_dir, "labels.csv")
    
    # Base algorithms
    algos = {
        "fib": [
            "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)",
            "def fibonacci(num):\n    if num <= 1: return num\n    return fibonacci(num-1) + fibonacci(num-2)",
            "def fib(n):\n    a, b = 0, 1\n    for _ in range(n): a, b = b, a+b\n    return a",
            "def f(x):\n    if x < 2: return x\n    a,b=0,1\n    for i in range(x):a,b=b,a+b\n    return a"
        ],
        "fact": [
            "def fact(n):\n    if n == 0: return 1\n    return n * fact(n-1)",
            "def factorial(x):\n    res = 1\n    for i in range(1, x+1): res *= i\n    return res",
            "import math\ndef fact(n):\n    return math.factorial(n)"
        ],
        "sort": [
            "def sort_arr(arr):\n    return sorted(arr)",
            "def bubble(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
            "def qsort(arr):\n    if len(arr) <= 1: return arr\n    p = arr[len(arr)//2]\n    l = [x for x in arr if x < p]\n    m = [x for x in arr if x == p]\n    r = [x for x in arr if x > p]\n    return qsort(l) + m + qsort(r)"
        ]
    }
    
    count = 0
    with open(labels_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pair_id", "label"])
        
        # Generate exact copies, renames, structural refactors (same algo, diff impl)
        for algo_name, impls in algos.items():
            for i in range(len(impls)):
                for j in range(i, len(impls)):
                    pair_id = f"oj_{count}"
                    with open(os.path.join(out_dir, f"{pair_id}_a.py"), "w") as fa:
                        fa.write(impls[i])
                    with open(os.path.join(out_dir, f"{pair_id}_b.py"), "w") as fb:
                        fb.write(impls[j])
                    
                    if i == j:
                        writer.writerow([pair_id, "exact_copy"])
                    else:
                        writer.writerow([pair_id, "structural_refactoring"])
                    count += 1
                    
        # Generate unrelated
        algo_keys = list(algos.keys())
        for _ in range(10):
            k1, k2 = random.sample(algo_keys, 2)
            pair_id = f"oj_{count}"
            with open(os.path.join(out_dir, f"{pair_id}_a.py"), "w") as fa:
                fa.write(random.choice(algos[k1]))
            with open(os.path.join(out_dir, f"{pair_id}_b.py"), "w") as fb:
                fb.write(random.choice(algos[k2]))
            writer.writerow([pair_id, "unrelated"])
            count += 1
            
    print(f"Generated {count} OJClone subset pairs in {out_dir}")

if __name__ == "__main__":
    generate_ojclone_subset()

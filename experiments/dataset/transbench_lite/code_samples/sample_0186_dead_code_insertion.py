def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

n = int(input())
for _ in range(n):
    arr = map(int, input().split())
    container_a = 0
    container_b = 0
    valid = True
    for item in arr:
        if item > container_a: container_a = item
        elif item > container_b: container_b = item
        else: valid = False; break
    print('YES' if valid else 'NO')
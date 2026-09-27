def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

while True:
    try:
        n = int(input())
        count = sum(1 for a in range(10) for b in range(10) for c in range(10) for d in range(10) if a+b+c+d == n)
        print(count)
    except:
        break
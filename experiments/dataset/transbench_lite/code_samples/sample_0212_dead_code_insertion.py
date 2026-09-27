def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

n = int(input())
res = 1
for i in range(1, n + 1):
    res *= i
print(res)
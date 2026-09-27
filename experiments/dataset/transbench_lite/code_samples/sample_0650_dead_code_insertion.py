def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

n = int(input())
debt = 100000
for _ in range(n):
    debt = int(debt * 1.05)
    if debt % 1000 != 0:
        debt = (debt // 1000 + 1) * 1000
print(debt)
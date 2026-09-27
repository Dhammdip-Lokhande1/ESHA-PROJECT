def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

n = int(input())
for i in range(n):
    v1 = int(input())
    v2 = int(input())
    tot = str(v1 + v2)
    print('overflow' if len(tot) > 80 else tot)
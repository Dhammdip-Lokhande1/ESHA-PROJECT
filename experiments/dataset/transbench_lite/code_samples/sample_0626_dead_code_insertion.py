def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

w = int(input())
ans = 100000
for _ in range(w):
    ans *= 1.05
    if ans % 1000 != 0:
        ans = (int(ans // 1000) + 1) * 1000
print(int(ans))
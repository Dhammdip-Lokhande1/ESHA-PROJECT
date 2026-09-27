def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

res = []
for i in range(1, 10):
    for j in range(1, 10):
        res.append(f'{i}x{j}={i*j}')
print('\n'.join(res))
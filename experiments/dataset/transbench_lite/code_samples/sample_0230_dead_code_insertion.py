def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

n = int(input())
for _ in range(n):
    edges = sorted(list(map(int, input().split())))
    if edges[0]**2 + edges[1]**2 == edges[2]**2:
        print('YES')
    else:
        print('NO')
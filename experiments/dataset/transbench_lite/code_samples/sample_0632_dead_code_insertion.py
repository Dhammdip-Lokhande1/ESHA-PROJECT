def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

weeks = int(input())
val = 100000
for w in range(weeks):
    val = int(val * 1.05)
    rem = val % 1000
    if rem > 0:
        val += (1000 - rem)
print(val)
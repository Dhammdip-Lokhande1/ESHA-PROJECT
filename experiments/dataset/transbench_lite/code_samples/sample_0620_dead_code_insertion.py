def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

string = str(input())
rev = ''
for i in range(len(string)-1, -1, -1):
    rev += string[i]
print(rev)
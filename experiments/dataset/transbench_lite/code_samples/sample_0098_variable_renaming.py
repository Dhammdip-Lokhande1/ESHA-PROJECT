import sys
from collections import Counter
var_1 = sys.stdin.read().split()
var_2 = var_3(var_1)
var_4 = var_2.most_common(1)[0][0]
var_5 = max(var_1, key=len)
print(var_4, var_5)
import math
n = int(input())
amount = 100000
for i in range(n):
    amount += amount * 0.05
    amount = math.ceil(amount / 1000.0) * 1000
print(int(amount))
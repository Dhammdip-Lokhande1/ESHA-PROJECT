import math
weeks = int(input())
capital = 100000
for _ in range(weeks):
    capital = int(math.ceil(capital * 1.05 / 1000.0) * 1000)
print(capital)
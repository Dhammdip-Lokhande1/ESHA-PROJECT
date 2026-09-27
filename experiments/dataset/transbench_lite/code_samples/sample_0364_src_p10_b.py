import sys
is_prime = [1]*1000000
is_prime[0] = is_prime[1] = 0
for i in range(2, 1000):
    if is_prime[i]:
        for j in range(i*i, 1000000, i):
            is_prime[j] = 0
import itertools
counts = list(itertools.accumulate(is_prime))
for line in sys.stdin:
    print(counts[int(line)])
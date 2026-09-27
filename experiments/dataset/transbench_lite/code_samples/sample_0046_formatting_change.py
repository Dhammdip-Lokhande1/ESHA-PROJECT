# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

import sys
lines = [int(line) for line in sys.stdin]
limit = max(lines) + 1 if lines else 2
primes = [True] * limit
primes[0] = primes[1] = False
for i in range(2, int(limit**0.5) + 1):
    if primes[i]:
        for j in range(i*i, limit, i):
            primes[j] = False
for n in lines:
    print(sum(primes[:n+1]))

# End of file

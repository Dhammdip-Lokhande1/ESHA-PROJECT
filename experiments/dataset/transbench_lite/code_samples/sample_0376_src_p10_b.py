import sys
MAX = 1000000
is_prime = [True] * MAX
is_prime[0] = is_prime[1] = False
for i in range(2, int(MAX**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, MAX, i):
            is_prime[j] = False
prefix = [0] * MAX
curr = 0
for i in range(MAX):
    if is_prime[i]: curr += 1
    prefix[i] = curr
for line in sys.stdin:
    print(prefix[int(line)])
import sys
def get_primes(limit):
    is_p = [True] * (limit + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, limit + 1, i):
                is_p[j] = False
    cum = [0] * (limit + 1)
    for i in range(1, limit + 1):
        cum[i] = cum[i-1] + (1 if is_p[i] else 0)
    return cum
cum = get_primes(999999)
for line in sys.stdin:
    print(cum[int(line)])
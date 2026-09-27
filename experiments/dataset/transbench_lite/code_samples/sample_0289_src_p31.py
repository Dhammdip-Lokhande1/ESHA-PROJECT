while True:
    n, s = map(int, input().split())
    if n == 0 and s == 0: break
    import itertools
    print(sum(1 for c in itertools.combinations(range(10), n) if sum(c) == s))
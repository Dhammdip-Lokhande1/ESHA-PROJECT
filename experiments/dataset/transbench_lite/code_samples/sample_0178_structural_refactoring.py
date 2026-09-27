import sys
for line in sys.stdin:
    n, s = map(int, line.split())
    if n == 0 and s == 0:
        break
    import itertools
    cnt = 0
    for combo in itertools.combinations(range(10), n):
        if sum(combo) == s:
            cnt += 1
    print(cnt)
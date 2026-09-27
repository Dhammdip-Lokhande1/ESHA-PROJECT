import sys
lines = sys.stdin.read().split()
for s in lines:
    c = sorted(map(int, s.split(',')))
    u = set(c)
    st = (len(u) == 5 and c[4] - c[0] == 4) or c == [1, 10, 11, 12, 13]
    counts = sorted([c.count(x) for x in u], reverse=True)
    if counts == [4, 1]: print('four card')
    elif counts == [3, 2]: print('full house')
    elif st: print('straight')
    elif counts == [3, 1, 1]: print('three card')
    elif counts == [2, 2, 1]: print('two pair')
    elif counts == [2, 1, 1, 1]: print('one pair')
    else: print('null')
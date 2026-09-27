import sys
for line in sys.stdin:
    try:
        h = list(map(int, line.split(',')))
        if len(h) < 5: continue
        h.sort()
        counts = sorted([h.count(x) for x in set(h)], reverse=True)
        st = (len(set(h)) == 5 and h[4] - h[0] == 4) or h == [1, 10, 11, 12, 13]
        if counts[0] == 4: print('four card')
        elif counts == [3, 2]: print('full house')
        elif st: print('straight')
        elif counts[0] == 3: print('three card')
        elif counts == [2, 2, 1]: print('two pair')
        elif counts[0] == 2: print('one pair')
        else: print('null')
    except:
        break
import sys
for line in sys.stdin:
    cards = list(map(int, line.split(',')))
    cards.sort()
    from collections import Counter
    freq = Counter(cards)
    mc = freq.most_common()
    is_str = (len(freq) == 5 and cards[4] - cards[0] == 4) or cards == [1, 10, 11, 12, 13]
    if mc[0][1] == 4: print('four card')
    elif mc[0][1] == 3 and mc[1][1] == 2: print('full house')
    elif is_str: print('straight')
    elif mc[0][1] == 3: print('three card')
    elif mc[0][1] == 2 and mc[1][1] == 2: print('two pair')
    elif mc[0][1] == 2: print('one pair')
    else: print('null')
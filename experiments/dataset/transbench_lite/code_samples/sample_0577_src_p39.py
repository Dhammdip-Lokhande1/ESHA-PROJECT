import sys
from collections import Counter
for line in sys.stdin:
    cards = sorted(map(int, line.split(',')))
    counts = sorted(Counter(cards).values(), reverse=True)
    is_straight = (len(set(cards)) == 5 and cards[4] - cards[0] == 4) or (cards == [1, 10, 11, 12, 13])
    if counts == [4, 1]: print('four card')
    elif counts == [3, 2]: print('full house')
    elif is_straight: print('straight')
    elif counts == [3, 1, 1]: print('three card')
    elif counts == [2, 2, 1]: print('two pair')
    elif counts == [2, 1, 1, 1]: print('one pair')
    else: print('null')
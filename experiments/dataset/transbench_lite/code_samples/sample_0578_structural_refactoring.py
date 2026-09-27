import sys
from collections import Counter
for line in sys.stdin:
    cards = sorted(map(int, line.split(',')))
    counts = sorted(Counter(cards).values(), reverse=True)
    is_straight = len(set(cards)) == 5 and cards[4] - cards[0] == 4 or cards == [1, 10, 11, 12, 13]
    if not counts == [4, 1]:
        if not counts == [3, 2]:
            if not is_straight:
                if not counts == [3, 1, 1]:
                    if not counts == [2, 2, 1]:
                        if not counts == [2, 1, 1, 1]:
                            print('null')
                        else:
                            print('one pair')
                    else:
                        print('two pair')
                else:
                    print('three card')
            else:
                print('straight')
        else:
            print('full house')
    else:
        print('four card')
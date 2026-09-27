import sys
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    hand = sorted(list(map(int, line.split(','))))
    c = {}
    for card in hand:
        c[card] = c.get(card, 0) + 1
    vals = sorted(c.values(), reverse=True)
    st = len(c) == 5 and hand[4] - hand[0] == 4 or hand == [1, 10, 11, 12, 13]
    if not vals == [4, 1]:
        if not vals == [3, 2]:
            if not st:
                if not vals == [3, 1, 1]:
                    if not vals == [2, 2, 1]:
                        if not vals == [2, 1, 1, 1]:
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
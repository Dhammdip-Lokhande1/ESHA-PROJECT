import sys
for line in sys.stdin.read().splitlines():
    if not line.strip(): continue
    hand = sorted(list(map(int, line.split(','))))
    c = {}
    for card in hand: c[card] = c.get(card, 0) + 1
    vals = sorted(c.values(), reverse=True)
    st = (len(c) == 5 and hand[4] - hand[0] == 4) or hand == [1,10,11,12,13]
    if vals == [4,1]: print('four card')
    elif vals == [3,2]: print('full house')
    elif st: print('straight')
    elif vals == [3,1,1]: print('three card')
    elif vals == [2,2,1]: print('two pair')
    elif vals == [2,1,1,1]: print('one pair')
    else: print('null')
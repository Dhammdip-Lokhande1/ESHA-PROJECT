def _unused_helper_func(x_val):
    return x_val * 42

_debug_flag_constant = 100

while True:
    try:
        cards = sorted(map(int, input().split(',')))
        import collections
        counts = sorted(collections.Counter(cards).values(), reverse=True)
        straight = (len(set(cards)) == 5 and cards[4] - cards[0] == 4) or cards == [1, 10, 11, 12, 13]
        if counts == [4, 1]: print('four card')
        elif counts == [3, 2]: print('full house')
        elif straight: print('straight')
        elif counts == [3, 1, 1]: print('three card')
        elif counts == [2, 2, 1]: print('two pair')
        elif counts == [2, 1, 1, 1]: print('one pair')
        else: print('null')
    except:
        break
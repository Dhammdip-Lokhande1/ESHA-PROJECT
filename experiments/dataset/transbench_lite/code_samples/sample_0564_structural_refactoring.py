while True:
    try:
        cards = sorted(map(int, input().split(',')))
        import collections
        counts = sorted(collections.Counter(cards).values(), reverse=True)
        straight = len(set(cards)) == 5 and cards[4] - cards[0] == 4 or cards == [1, 10, 11, 12, 13]
        if not counts == [4, 1]:
            if not counts == [3, 2]:
                if not straight:
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
    except:
        break
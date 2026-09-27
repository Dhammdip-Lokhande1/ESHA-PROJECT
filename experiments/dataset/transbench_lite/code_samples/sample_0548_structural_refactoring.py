import sys
for line in sys.stdin:
    try:
        h = list(map(int, line.split(',')))
        if len(h) < 5:
            continue
        h.sort()
        counts = sorted([h.count(x) for x in set(h)], reverse=True)
        st = len(set(h)) == 5 and h[4] - h[0] == 4 or h == [1, 10, 11, 12, 13]
        if not counts[0] == 4:
            if not counts == [3, 2]:
                if not st:
                    if not counts[0] == 3:
                        if not counts == [2, 2, 1]:
                            if not counts[0] == 2:
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
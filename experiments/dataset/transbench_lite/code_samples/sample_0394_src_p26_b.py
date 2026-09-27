while True:
    try:
        a = list(map(int, input().split()))
        b = list(map(int, input().split()))
        hits = sum(1 for i in range(4) if a[i] == b[i])
        blows = sum(1 for x in b if x in a) - hits
        print(hits, blows)
    except:
        break
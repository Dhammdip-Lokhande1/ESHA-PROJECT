while True:
    try:
        v = float(input())
        y = 4.9 * (v / 9.8) ** 2
        ans = 2
        while 5 * ans - 5 < y:
            ans += 1
        print(ans)
    except:
        break
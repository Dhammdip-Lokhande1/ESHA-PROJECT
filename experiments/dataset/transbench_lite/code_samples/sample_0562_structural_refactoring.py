while True:
    m, d = map(int, input().split())
    if m == 0:
        break
    import datetime
    print(datetime.date(2004, m, d).strftime('%A'))
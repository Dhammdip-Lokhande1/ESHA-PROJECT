import sys
for line in sys.stdin:
    month, day = map(int, line.split())
    if month == 0: break
    import datetime
    w = datetime.date(2004, month, day).strftime('%A')
    print(w)
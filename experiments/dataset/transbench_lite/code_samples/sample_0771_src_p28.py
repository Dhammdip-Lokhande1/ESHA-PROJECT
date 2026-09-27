import datetime, sys
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for line in sys.stdin:
    m, d = map(int, line.split())
    if m == 0: break
    dt = datetime.date(2004, m, d)
    print(days[dt.weekday()])
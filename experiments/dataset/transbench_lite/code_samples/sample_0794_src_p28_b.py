import datetime, sys
week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
lines = sys.stdin.read().split()
i = 0
while i < len(lines):
    m, d = int(lines[i]), int(lines[i+1])
    if m == 0: break
    i += 2
    print(week[datetime.date(2004, m, d).weekday()])
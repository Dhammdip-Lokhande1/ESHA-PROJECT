import sys
days_in_months = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
name = ['Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday']
for line in sys.stdin:
    m, d = map(int, line.split())
    if m == 0: break
    day_count = sum(days_in_months[:m]) + d - 1
    print(name[day_count % 7])
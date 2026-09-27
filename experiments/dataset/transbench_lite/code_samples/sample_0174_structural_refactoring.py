import sys
ls = []
for row in sys.stdin.read().splitlines():
    if row:
        num = int(row)
        if not num == 0:
            ls.append(num)
        else:
            print(ls.pop())
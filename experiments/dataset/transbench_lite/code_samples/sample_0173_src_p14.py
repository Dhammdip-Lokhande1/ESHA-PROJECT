import sys
ls = []
for row in sys.stdin.read().splitlines():
    if row:
        num = int(row)
        if num == 0:
            print(ls.pop())
        else:
            ls.append(num)
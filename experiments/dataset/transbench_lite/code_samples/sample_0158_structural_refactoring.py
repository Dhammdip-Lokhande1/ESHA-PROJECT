import sys
for row in sys.stdin.read().splitlines():
    if row:
        n1, n2 = map(int, row.split())
        print(len(str(n1 + n2)))
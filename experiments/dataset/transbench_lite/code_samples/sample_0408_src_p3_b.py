import sys
for line in sys.stdin.readlines():
    v1, v2 = [int(x) for x in line.split()]
    print(len(str(v1 + v2)))
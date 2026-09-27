import sys
stk = []
for x in map(int, sys.stdin.read().split()):
    if not x == 0:
        stk.append(x)
    else:
        print(stk.pop())
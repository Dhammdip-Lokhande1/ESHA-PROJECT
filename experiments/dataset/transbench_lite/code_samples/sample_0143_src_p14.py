import sys
stack = []
for line in sys.stdin:
    num = int(line)
    if not num: print(stack.pop())
    else: stack.append(num)
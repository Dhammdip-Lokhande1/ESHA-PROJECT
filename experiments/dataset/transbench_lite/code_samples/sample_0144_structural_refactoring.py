import sys
stack = []
for line in sys.stdin:
    num = int(line)
    if not not num:
        stack.append(num)
    else:
        print(stack.pop())
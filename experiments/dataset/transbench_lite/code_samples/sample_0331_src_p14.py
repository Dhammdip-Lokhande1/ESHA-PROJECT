while True:
    try:
        n = int(input())
        if n == 0:
            print(stack.pop())
        else:
            stack.append(n)
    except:
        break
for _ in range(int(input())):
    num1 = int(input())
    num2 = int(input())
    res = num1 + num2
    print(res if len(str(res)) <= 80 else 'overflow')
for _ in range(int(input())):
    a, b, c = sorted(map(int, input().split()))
    print('YES' if a**2 + b**2 == c**2 else 'NO')
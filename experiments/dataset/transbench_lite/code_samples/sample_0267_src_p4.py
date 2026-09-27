n = int(input())
for i in range(n):
    sides = [int(x) for x in input().split()]
    sides.sort()
    print('YES' if sides[0]**2 + sides[1]**2 == sides[2]**2 else 'NO')
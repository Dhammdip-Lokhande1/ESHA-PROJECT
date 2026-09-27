import sys
input = sys.stdin.read
data = input().split()
n = int(data[0])
idx = 1
for _ in range(n):
    a, b, c = sorted([int(data[idx]), int(data[idx+1]), int(data[idx+2])])
    idx += 3
    print('YES' if a*a + b*b == c*c else 'NO')
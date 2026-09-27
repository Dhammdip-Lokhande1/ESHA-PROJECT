import sys
N = 1000000
p = [1]*N
p[0] = p[1] = 0
for i in range(2, 1000):
    if p[i]:
        for j in range(i*i, N, i):
            p[j] = 0
acc = [0]*N
for i in range(1, N):
    acc[i] = acc[i-1] + p[i]
for l in sys.stdin:
    print(acc[int(l)])
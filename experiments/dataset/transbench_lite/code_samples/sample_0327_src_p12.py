w = int(input())
n = int(input())
ans = [i for i in range(1, w+1)]
for _ in range(n):
    a, b = map(int, input().split(','))
    ans[a-1], ans[b-1] = ans[b-1], ans[a-1]
for x in ans: print(x)
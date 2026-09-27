w = int(input())
ans = 100000
for _ in range(w):
    ans *= 1.05
    if ans % 1000 != 0:
        ans = (int(ans // 1000) + 1) * 1000
print(int(ans))
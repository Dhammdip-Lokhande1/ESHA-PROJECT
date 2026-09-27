heights = [int(input()) for _ in range(10)]
heights.sort(reverse=True)
for h in heights[:3]:
    print(h)
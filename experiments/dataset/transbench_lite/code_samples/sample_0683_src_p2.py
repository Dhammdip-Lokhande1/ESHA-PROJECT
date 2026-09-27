h = []
for _ in range(10):
    h.append(int(input()))
h.sort(reverse=True)
print(*h[:3], sep='\n')
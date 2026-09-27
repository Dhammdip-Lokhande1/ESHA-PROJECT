lst = []
for i in range(10):
    lst.append(int(input()))
sorted_lst = sorted(lst, reverse=True)
for item in sorted_lst[:3]:
    print(item)
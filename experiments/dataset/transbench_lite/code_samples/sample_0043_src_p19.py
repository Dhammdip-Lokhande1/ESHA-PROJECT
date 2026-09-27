arr = [int(x) for x in input().split()]
arr.sort()
print(*reversed(arr))
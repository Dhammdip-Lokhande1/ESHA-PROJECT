import sys
data = [int(x) for x in sys.stdin.read().split()]
i = 0
while i < len(data):
    n = data[i]
    if n == 0: break
    arr = data[i+1:i+1+n]
    i += 1 + n
    mx = curr = arr[0]
    for item in arr[1:]:
        curr = max(item, curr + item)
        mx = max(mx, curr)
    print(mx)
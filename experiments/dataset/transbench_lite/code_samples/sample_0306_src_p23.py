import sys
while True:
    n = int(sys.stdin.readline())
    if n == 0: break
    arr = [int(sys.stdin.readline()) for _ in range(n)]
    max_sum = cur_sum = arr[0]
    for x in arr[1:]:
        cur_sum = max(x, cur_sum + x)
        max_sum = max(max_sum, cur_sum)
    print(max_sum)
import sys
def kadane(arr):
    max_so_far = arr[0]
    curr_max = arr[0]
    for i in range(1, len(arr)):
        curr_max = max(arr[i], curr_max + arr[i])
        max_so_far = max(max_so_far, curr_max)
    return max_so_far
lines = sys.stdin.read().split()
idx = 0
while idx < len(lines):
    n = int(lines[idx])
    if n == 0: break
    nums = [int(x) for x in lines[idx+1:idx+1+n]]
    idx += 1 + n
    print(kadane(nums))
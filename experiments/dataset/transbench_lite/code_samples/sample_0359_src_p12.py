w = int(input())
n = int(input())
nums = list(range(1, w + 1))
for i in range(n):
    pair = input().split(',')
    a, b = int(pair[0]) - 1, int(pair[1]) - 1
    nums[a], nums[b] = nums[b], nums[a]
for val in nums:
    print(val)
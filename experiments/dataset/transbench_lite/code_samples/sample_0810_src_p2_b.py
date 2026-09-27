import heapq
nums = [int(input()) for _ in range(10)]
for x in heapq.nlargest(3, nums):
    print(x)
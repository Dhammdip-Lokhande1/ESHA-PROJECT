import sys
w = int(sys.stdin.readline())
n = int(sys.stdin.readline())
arr = [i + 1 for i in range(w)]
for _ in range(n):
    u, v = [int(x) for x in sys.stdin.readline().split(',')]
    arr[u - 1], arr[v - 1] = arr[v - 1], arr[u - 1]
print(*arr, sep='\n')
import sys
lines = sys.stdin.read().split()
for s in lines:
    arr = [int(x) for x in s.split(',')]
    dist = arr[:10]
    v1, v2 = arr[10], arr[11]
    target = sum(dist) * v1 / (v1 + v2)
    cum = 0
    for idx, d in enumerate(dist, 1):
        cum += d
        if cum >= target:
            print(idx)
            break
import sys
lines = sys.stdin.read().split()
for i in range(0, len(lines), 8):
    a = [int(x) for x in lines[i:i+4]]
    b = [int(x) for x in lines[i+4:i+8]]
    hit = sum(a[j] == b[j] for j in range(4))
    blow = len(set(a) & set(b)) - hit
    print(hit, blow)
import sys
for _ in range(int(sys.stdin.readline())):
    x = int(sys.stdin.readline())
    y = int(sys.stdin.readline())
    ans = x + y
    print(ans if len(str(ans)) <= 80 else 'overflow')
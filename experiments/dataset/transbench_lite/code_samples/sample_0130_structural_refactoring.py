import sys
print(*sorted(map(int, sys.stdin.read().split()), reverse=True))
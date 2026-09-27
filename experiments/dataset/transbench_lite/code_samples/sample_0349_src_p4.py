import sys
for line in sys.stdin.readlines()[1:]:
    s = sorted(map(int, line.split()))
    print('YES' if s[0]**2 + s[1]**2 == s[2]**2 else 'NO')
import sys
rect = 0; lozenge = 0
for line in sys.stdin:
    a, b, c = map(int, line.split(','))
    if a*a + b*b == c*c:
        rect += 1
    elif a == b:
        lozenge += 1
print(rect)
print(lozenge)
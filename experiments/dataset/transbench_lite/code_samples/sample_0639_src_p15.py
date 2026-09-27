import sys
for line in sys.stdin:
    step = int(line)
    print(sum((x**2)*step for x in range(step, 600, step)))
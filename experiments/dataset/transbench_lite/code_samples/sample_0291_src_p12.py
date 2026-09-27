import sys
lines = sys.stdin.read().splitlines()
if lines:
    w = int(lines[0])
    n = int(lines[1])
    state = list(range(1, w + 1))
    for idx in range(2, 2 + n):
        u, v = map(int, lines[idx].split(','))
        state[u-1], state[v-1] = state[v-1], state[u-1]
    print('\n'.join(map(str, state)))
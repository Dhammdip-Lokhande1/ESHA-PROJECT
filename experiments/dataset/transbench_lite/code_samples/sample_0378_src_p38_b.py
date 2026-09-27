import sys
data = sys.stdin.read().splitlines()
if len(data) >= 9:
    h_w = data[:5]
    v_w = data[5:9]
    res = 'RRRRDDDDLLLLUUUU'
    print(res)
import sys
text = sys.stdin.read().split()
c = {}
for w in text:
    c[w] = c.get(w, 0) + 1
frequent = sorted(c.items(), key=lambda x: x[1], reverse=True)[0][0]
longest = sorted(text, key=len, reverse=True)[0]
print(frequent, longest)
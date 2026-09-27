import sys
words = sys.stdin.read().split()
freq = {}
for w in words:
    freq[w] = freq.get(w, 0) + 1
max_w = max(freq, key=freq.get)
long_w = max(words, key=len)
print(max_w, long_w)
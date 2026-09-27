import sys
from collections import Counter
words = sys.stdin.read().split()
counts = Counter(words)
most_freq = counts.most_common(1)[0][0]
longest = max(words, key=len)
print(most_freq, longest)
import sys
words = sys.stdin.readline().split()
max_len_word = ''
word_counts = {}
for w in words:
    word_counts[w] = word_counts.get(w, 0) + 1
    if len(w) > len(max_len_word):
        max_len_word = w
most_common = max(word_counts, key=lambda k: word_counts[k])
print(most_common, max_len_word)
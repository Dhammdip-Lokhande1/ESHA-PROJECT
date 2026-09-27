import sys
tokens = sys.stdin.read().split()
freq_token = max(set(tokens), key=tokens.count)
long_token = max(tokens, key=len)
print(freq_token, long_token)
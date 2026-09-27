line = input()
res = ''
for c in line:
    if not 'a' <= c <= 'z':
        res += c
    else:
        res += chr(ord(c) - 32)
print(res)
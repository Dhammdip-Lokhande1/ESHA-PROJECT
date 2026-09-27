line = input()
res = ''
for c in line:
    if 'a' <= c <= 'z':
        res += chr(ord(c) - 32)
    else:
        res += c
print(res)
string = str(input())
rev = ''
for i in range(len(string)-1, -1, -1):
    rev += string[i]
print(rev)
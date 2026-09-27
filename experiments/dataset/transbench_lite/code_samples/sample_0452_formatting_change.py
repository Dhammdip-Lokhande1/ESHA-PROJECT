# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

weeks = int(input())
val = 100000
for w in range(weeks):
    val = int(val * 1.05)
    rem = val % 1000
    if rem > 0:
        val += (1000 - rem)
print(val)

# End of file

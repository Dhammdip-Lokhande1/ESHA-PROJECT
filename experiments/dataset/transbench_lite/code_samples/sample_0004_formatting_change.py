# EHSA TransBench-Lite Formatting Transformation
# Author Solution - Refactored Layout

res = []
for i in range(1, 10):
    for j in range(1, 10):
        res.append(f'{i}x{j}={i*j}')
print('\n'.join(res))

# End of file

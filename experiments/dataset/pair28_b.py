import bisect
def search(arr, x):
    '''AI suggested using bisect for binary search.'''
    i = bisect.bisect_left(arr, x)
    if i != len(arr) and arr[i] == x:
        return i
    return -1
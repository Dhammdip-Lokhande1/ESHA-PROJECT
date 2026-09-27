def search(sorted_collection, query_item):
    low_bound = 0
    high_bound = len(sorted_collection) - 1
    while low_bound <= high_bound:
        middle_pos = (low_bound + high_bound) // 2
        if sorted_collection[middle_pos] == query_item:
            return middle_pos
        elif sorted_collection[middle_pos] < query_item:
            low_bound = middle_pos + 1
        else:
            high_bound = middle_pos - 1
    return -1

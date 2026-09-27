def selection_sort(unsorted_nums):
    list_size = len(unsorted_nums)
    for current_step in range(list_size):
        smallest_pos = current_step
        for candidate_pos in range(current_step + 1, list_size):
            if unsorted_nums[candidate_pos] < unsorted_nums[smallest_pos]:
                smallest_pos = candidate_pos
        unsorted_nums[current_step], unsorted_nums[smallest_pos] = unsorted_nums[smallest_pos], unsorted_nums[current_step]
    return unsorted_nums

def insertion_sort(target_array):
    for curr_pos in range(1, len(target_array)):
        element_to_insert = target_array[curr_pos]
        scan_idx = curr_pos - 1
        while scan_idx >= 0 and target_array[scan_idx] > element_to_insert:
            target_array[scan_idx + 1] = target_array[scan_idx]
            scan_idx -= 1
        target_array[scan_idx + 1] = element_to_insert
    return target_array

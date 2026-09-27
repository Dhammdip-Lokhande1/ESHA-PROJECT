def merge_sorted_pairs(first_list, second_list):
    idx_a, idx_b = 0, 0
    merged_output = []
    while idx_a < len(first_list) and idx_b < len(second_list):
        if first_list[idx_a] < second_list[idx_b]:
            merged_output.append(first_list[idx_a])
            idx_a += 1
        else:
            merged_output.append(second_list[idx_b])
            idx_b += 1
    merged_output.extend(first_list[idx_a:])
    merged_output.extend(second_list[idx_b:])
    return merged_output

def merge_sorted(l1, l2):
    return merge_sorted_pairs(l1, l2)

def sort_array(items_list):
    total_elements = len(items_list)
    for outer_idx in range(total_elements):
        for inner_idx in range(0, total_elements - outer_idx - 1):
            if items_list[inner_idx] > items_list[inner_idx + 1]:
                items_list[inner_idx], items_list[inner_idx + 1] = items_list[inner_idx + 1], items_list[inner_idx]
    return items_list

def find_indices(source_sequence, goal_value):
    start_pos = -1
    end_pos = -1
    for index_counter in range(len(source_sequence)):
        if source_sequence[index_counter] == goal_value:
            if start_pos == -1:
                start_pos = index_counter
            end_pos = index_counter
    return (start_pos, end_pos)

def purge_repeated_elements(input_collection):
    visited_set = set()
    unique_sequence = []
    for val in input_collection:
        if val not in visited_set:
            visited_set.add(val)
            unique_sequence.append(val)
    return unique_sequence

def remove_duplicates(items):
    return purge_repeated_elements(items)

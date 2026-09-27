def unpack_structure(multi_level_data):
    flat_collection = []
    for element in multi_level_data:
        if isinstance(element, list):
            flat_collection.extend(unpack_structure(element))
        else:
            flat_collection.append(element)
    return flat_collection

def flatten(nested_list):
    return unpack_structure(nested_list)

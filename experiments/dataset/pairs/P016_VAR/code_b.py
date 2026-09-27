def encode_runs(raw_sequence):
    if not raw_sequence:
        return []
    encoded_pairs = []
    active_character = raw_sequence[0]
    sequence_length = 1
    for symbol in raw_sequence[1:]:
        if symbol == active_character:
            sequence_length += 1
        else:
            encoded_pairs.append((active_character, sequence_length))
            active_character = symbol
            sequence_length = 1
    encoded_pairs.append((active_character, sequence_length))
    return encoded_pairs

def rle_encode(s):
    return encode_runs(s)

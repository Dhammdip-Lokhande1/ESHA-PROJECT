def calculate_word_frequencies(raw_sentence):
    token_list = raw_sentence.split()
    occurrence_map = {}
    for token in token_list:
        if token in occurrence_map:
            occurrence_map[token] += 1
        else:
            occurrence_map[token] = 1
    return occurrence_map

def word_freq(text):
    return calculate_word_frequencies(text)

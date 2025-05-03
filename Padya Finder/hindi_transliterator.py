import json

# Function to read vocabulary
with open('./datasets/hindi_vocab.json') as file:
    word_str = file.read()
    hindi_vocab = json.loads(word_str)

with open('./datasets/eng_to_hindi.json') as file:
    mapping_str = file.read()
    mapping = json.loads(mapping_str)

# Function to transliterate word
def transliterate_word(word, dry_run = False):
    # x = input()
    if dry_run:
        print('\n\n-----------------------------')
        print('Word: ', word)
    if len(word) == 0:
        return []
    if len(word) == 1:
        if word not in mapping.keys():
            return []
        return [mapped_w for mapped_w in mapping[word] if '्' not in mapped_w]
    current_mappings = []
    window_length = 3
    second_letter = word[1]
    if second_letter in ['r', 'h']:
        window_length = 4
    # In case you almost reached the end of string
    window_length = min(window_length, len(word))
    while window_length > 0:
        if dry_run: print('Window Length: ', window_length)
        window_word = word[0: window_length]
        if dry_run: print('Window Word: ', window_word)
        if window_word not in mapping: 
            if dry_run: print('Window Word is invalid')
            window_length = window_length - 1
            continue
        trans_words_for_window = mapping[window_word]
        if dry_run: print('Trans Words for Window Word: ', trans_words_for_window)
        remaining_word = word[window_length: ]
        if dry_run: print('Remaining Word: ', remaining_word)
        if dry_run: print('Finding the trans words for remaining word ...')
        if len(remaining_word) == 0:
            if (len(window_word) == 3 and window_word[-2:] == 'an') or (len(window_word) == 2 and window_word[-1] == 'n'):
                window_length = window_length - 1
                continue
            else:
                return trans_words_for_window
        else:
            trans_words_for_remaining = transliterate_word(remaining_word, dry_run)
        if dry_run: print('Trans Words for Remaining Word: ', trans_words_for_remaining)
        for trans_word_p1 in trans_words_for_window:
            for trans_word_p2 in trans_words_for_remaining:
                joined_word = trans_word_p1 + trans_word_p2
                current_mappings.append(joined_word)
                if dry_run: print('Current Mappings: ', current_mappings)
        if (len(window_word) == 3 and window_word[-2:] == 'an') or (len(window_word) == 2 and window_word[-1] == 'n'):
            window_length = window_length - 1
            continue
        else:
            break
    return current_mappings

# Function to get devanagari suggestions for the input word
def get_devanagari_suggestions(word):
    hindi_tokens = transliterate_word(word)
    valid_tokens = [token for token in hindi_tokens if token in hindi_vocab]
    if len(valid_tokens) == 0:
        return hindi_tokens
    else:
        return valid_tokens
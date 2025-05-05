import re
import json

# Function to read vocabulary
with open('./datasets/hindi_vocab.json') as file:
    word_str = file.read()
    hindi_vocab = json.loads(word_str)

with open('./datasets/char_hinglish_to_hindi.json') as file:
    ch_mapping_str = file.read()
    ch_mapping = json.loads(ch_mapping_str)

with open('./datasets/word_hinglish_to_hindi.json') as file:
    word_mapping_str = file.read()
    word_mapping = json.loads(word_mapping_str)


# Function to tokenize sentences
def tokenize_sentence(
    sentence: str = None, 
    lang: str = 'hinglish'
) -> list:
    """
        lang = 'hinglish' mean both hindi and english
             = 'hin'/'hindi'/'devanagari'/'dev'/'devanagri' mean only hindi
             = 'eng'/'english' mean only english
    """
    tokens = re.split(r'\s', sentence)
    invalid_char_regex = r'[^a-zA-Z\u0900-\u097F\u200c\u200d]'
    if lang in ['hin', 'hindi', 'devanagari', 'dev', 'devanagri']:
        invalid_char_regex = r'[^\u0900-\u097F\u200c\u200d]'
    elif lang in ['eng', 'english']:
        invalid_char_regex = r'[^a-zA-Z]'
    tokens = [re.sub(invalid_char_regex, '', token) for token in tokens if token != '']
    return tokens


# Function to transliterate word
def transliterate_word(
    word: str = None, 
    dry_run: bool = False
) -> list:    # x = input()
    if dry_run:
        print('\n\n-----------------------------')
        print('Word: ', word)
    # If word-level transliteration possible
    if word in word_mapping.keys():
        if dry_run: print('Word found in hinglish to hindi word mapping')
        return [word_mapping[word]]
    # Otherwise perform character-level transliteration
    if len(word) == 0:
        if dry_run: print('Word length is 0')
        return []
    if len(word) == 1 and word in ch_mapping:
        if dry_run: print('Word length is 1')
        return [mapped_w for mapped_w in ch_mapping[word] if '्' not in mapped_w]
    if len(word) == 2 and len(word.strip()) == 2:
        if dry_run: print('Word length is 2')
        if (word.endswith('a') or word.endswith('i') or word.endswith('u')) and len(ch_mapping[word]) <= 2:
            if dry_run: print('Word ends with a vowel so handling directly')
            return [ch_mapping[word][-1]]
        if (word.endswith('o') or word.endswith('e')) and len(ch_mapping[word]) <= 2:
            if dry_run: print('Word ends with a vowel so handling directly')
            return [ch_mapping[word][0]]

    current_mappings = []
    window_length = 3
    if len(word) >=2:
        second_letter = word[1]
        if second_letter in ['r', 'h']:
            window_length = 4
    if len(word) >= 4 and word[3] == 'n':
        window_length = 4
    # In case you almost reached the end of string
    window_length = min(window_length, len(word))
    while window_length > 0:
        if dry_run: print('Window Length: ', window_length)
        window_word = word[0: window_length]
        if dry_run: print('Window Word: ', window_word)
        if window_word in word_mapping.values():
            if dry_run: print('Window Word is a valid hindi word')
            trans_words_for_window = [window_word]
        elif len(window_word) == 1 and re.search(r'[\u0900-\u097F\u200c\u200d]', window_word):
            if dry_run: print('Window Word is a valid hindi character')
            trans_words_for_window = [window_word]    
        elif window_word in ch_mapping:
            if dry_run: print('Window Word found in hinglish to hindi character mapping')
            trans_words_for_window = ch_mapping[window_word]
        else:
            if dry_run: print('Window Word is invalid')
            window_length = window_length - 1
            continue
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


# Function to transliterate sentences
def transliterate_sentence(
    sentence: str = None, 
    dry_run: bool = False
) -> list:
    eng_tokens = tokenize_sentence(sentence)
    for i, token in enumerate(eng_tokens):
        if token in word_mapping:
            eng_tokens[i] = word_mapping[token]
        if len(token) == 2:
            if (token.endswith('a') or token.endswith('i') or token.endswith('u')) and len(ch_mapping[token]) <= 2:
                eng_tokens[i] = ch_mapping[token][-1]
            if (token.endswith('o') or token.endswith('e')) and len(ch_mapping[token]) <= 2:
                eng_tokens[i] = ch_mapping[token][0]
    mid_sent = ' '.join(eng_tokens)
    if dry_run: print('Mapped sentence: ', mid_sent)
    hindi_sent_list = [mid_sent]
    if re.search(r'[a-zA-Z]', mid_sent):
        hindi_sent_list = transliterate_word(mid_sent, dry_run=dry_run)
    valid_sent_list = []
    if dry_run: print('\n\n')
    for i, hindi_sent in enumerate(hindi_sent_list):
        if dry_run: print(f'\n\nHindi sentence possibility {i+1}: ', hindi_sent)
        hin_tokens = tokenize_sentence(hindi_sent, 'hin')
        invalid_sent = False
        for token in hin_tokens:
            if token not in hindi_vocab or token.endswith('्'):
                if dry_run: print('This sentence possibility is invalid due to the token ', token)
                invalid_sent = True
                break
        if not invalid_sent:
            if dry_run: print('This sentence possibility is valid')
            valid_sent_list.append(hindi_sent)
    if len(valid_sent_list) == 0:
        return hindi_sent_list
    else:
        return valid_sent_list


# Function to get devanagari suggestions for the input sentence
def get_devanagari_suggestions(sentence: str = None) -> list:
    return transliterate_sentence(sentence)
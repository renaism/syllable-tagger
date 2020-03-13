from nltk.util import pad_sequence

'''
Desc: Convert syllable-segmented text to tokens of tags
In  : data_train (pd.DataFrame)
Out: List
'''
def tokenize(data_train):
    tokens = []

    for syl_word in data_train['syllables']:
        # Split words that have hyphen
        syl_sub_words  = syl_word.replace('-', ' ').split() 

        for syl_sub_word in syl_sub_words:
            n = len(syl_sub_word)
            word_tokens = []

            for i in range(n):
                # Skip if the current char is a syllable boundary
                if syl_sub_word[i] == '.':
                    continue
                # Last char is always a syllable-end
                if i == n-1:
                    token = syl_sub_word[i] + '*'
                # If next char is a syllable boundary
                elif syl_sub_word[i+1] == '.':
                    token = syl_sub_word[i] + '*'
                # If next char is not syllable boundary
                else:
                    token = syl_sub_word[i] + '!'
                word_tokens.append(token)
            
            tokens.append(word_tokens)
    
    return tokens


'''
Desc: Pad the beginning of each word with n number of token '#' and the ending with an end marker
In  : tokens (List), n (int), start_pad (bool), end_marker (bool)
Out : List
'''
def pad_tokens(tokens, n, start_pad=True, end_marker=True):
    assert start_pad or end_marker
    
    # Add front padding
    if start_pad:
        padded_tokens = [list(pad_sequence(wt, n, pad_left=True, left_pad_symbol='#')) for wt in tokens]
    
    # Add end marker
    if end_marker:
        padded_tokens = [wt + ['$'] for wt in padded_tokens]
    
    return padded_tokens
import utility as util
import pandas as pd
import re

from config import *

CONSONANT_SWAP_MAP = {
    'b': 'p', 'p': 'b',
    'd': 't', 't': 'd',
    'k': 'q', 'q': 'k',
    'c': 'j', 'j': 'c',
    'f': 'v', 'v': 'f',
    's': 'z', 'z': 's',
    'l': 'r', 'r': 'l',
}

'''
Desc: Extract the onset, nucleus, and coda from a valid syllable
In  : syllable (str)
Out : tuple
'''
def extract_syllable(syllable, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT):
    # Check nucleus containing diphtongs
    nuc_match = re.search(r'{}'.format('|'.join(diphtongs)), syllable)

    # Check nucleus containing vowels from letters a, e, i, o, u
    if not nuc_match:
        nuc_match = re.search(r'[{}]+'.format(''.join(vowels)), syllable)
    
    # Check for letter y as a semi-vocal
    if not nuc_match:
        for semi_vowel in semi_vowels:
            nuc_match = re.search(r'\B{}+'.format(semi_vowel), syllable)

            if nuc_match:
                break
    
    if nuc_match:
        onset   = syllable[:nuc_match.start()]
        nucleus = syllable[nuc_match.start():nuc_match.end()]
        coda    = syllable[nuc_match.end():]
    else:
        onset   = syllable
        nucleus = ''
        coda    = ''

    return (onset, nucleus, coda) 


'''
Desc: Generate new word by flipping the onset of the 1st and 2nd syllable
In  : syl_word (str)
Out : tuple
'''
def flip_onsets_word(syl_word, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT):
    # Convert syllable-segmented text to a list
    syllables = util.split_syllables(syl_word)
    
    # Skip if word only has one syllable
    if len(syllables) < 2:
        return
    
    # Extract the 1st and 2nd syllables
    syl_0 = extract_syllable(syllables[0], vowels=vowels, semi_vowels=semi_vowels, diphtongs=diphtongs)
    syl_1 = extract_syllable(syllables[1], vowels=vowels, semi_vowels=semi_vowels, diphtongs=diphtongs)

    # Skip if one or both syllable doesn't have an onset, or both onsets are the same
    if syl_0[0] == '' or syl_1[0] == '' or syl_0[0] == syl_1[0]:
        return
    
    # Skip if one of the onsets is a punctuation mark
    if syl_0[0] == "'" or syl_1[0] == "'":
        return
    
    # Flip the onset of the two syllables
    syllables[0] = syl_1[0] + syl_0[1] + syl_0[2]
    syllables[1] = syl_0[0] + syl_1[1] + syl_1[2]
    
    # Convert syllables to string
    new_syl  = util.syllables_to_text(syllables)
    new_word = util.syllables_to_word(syllables)
    
    return (new_word, new_syl)


'''
Desc: Batch for flip_onsets_word with a set of words
In  : data_train (pd.DataFrame)
Out : pd.DataFrame
'''
def flip_onsets(data_train, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT, stop=lambda: False):
    # List for storing new words
    new_data = []

    for syl_word in data_train['syllables']:
        if stop():
            return
        
        flipped_word = flip_onsets_word(syl_word, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT)

        if flipped_word:
            new_data.append(flipped_word)
    
    # Convert to DataFrame and return it
    return pd.DataFrame(new_data, columns=['word', 'syllables'])


'''
Desc: Generate new words by swapping consonants in the word with another consonant
In  : syl_word (str)
Out : list
'''
def swap_consonants_word(syl_word):
    # Convert syllable-segmented text to a list
    letters = list(syl_word)
    
    # Find all position of consonants that are swappable
    swap_pos = []

    for i in range(len(letters)):
        if letters[i] in CONSONANT_SWAP_MAP:
            swap_pos.append(i)
    
    # Number of possible variations
    n = 2**len(swap_pos)
    
    # Create a binary swap map
    bin_format ='0{}b'.format(len(bin(n-1)[2:]))
    swap_map = []

    for i in range(n):
        # Skip all 0 swap map (no swap / original word)
        if i == 0:
            continue

        swap_map.append([int(x) for x in format(i, bin_format)])
    
    # Swap the consonant based on the swap map
    swapped_words = []

    for sm_row in swap_map:
        new_letters = letters[:]

        for i, swap in enumerate(sm_row):
            if swap == 1:
                swapped_letter = new_letters[swap_pos[i]]
                new_letters[swap_pos[i]] = CONSONANT_SWAP_MAP[swapped_letter]
        
        # Append consonant-swapped word to the array
        new_syl = ''.join(new_letters)
        new_word = new_syl.replace('.', '')
        swapped_words.append((new_word, new_syl))
    
    return swapped_words


    
'''
Desc: Batch for swap_consonants_word with a set of words
In  : data_train (pd.DataFrame)
Out : pd.DataFrame
'''
def swap_consonants(data_train, stop=lambda: False):
    new_data = []

    for syl_word in data_train['syllables']:
        if stop():
            return
        
        new_data += swap_consonants_word(syl_word)
    
    # Convert to DataFrame and return it
    return pd.DataFrame(new_data, columns=['word', 'syllables'])


'''
Desc: Generate new word by transposing nucleus in the word
In  : syl_word (str)
Out : tuple
'''
def transpose_nucleus_word(syl_word, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT):
    # Convert syllable-segmented text to a list
    syllables = util.split_syllables(syl_word)
    
    # Skip if word only has one syllable
    if len(syllables) < 2:
        return
    
    # Extract the 1st and 2nd syllables
    syl_0 = extract_syllable(syllables[0], vowels=vowels, semi_vowels=semi_vowels, diphtongs=diphtongs)
    syl_1 = extract_syllable(syllables[1], vowels=vowels, semi_vowels=semi_vowels, diphtongs=diphtongs)

    # Skip if one or both syllable doesn't have a nucleus, or both nucleus are the same
    if syl_0[1] == '' or syl_1[1] == '' or syl_0[1] == syl_1[1]:
        return
        
    # Skip if one or both syllable have more than one vowel
    if extract_syllable(syl_0[2])[1] != '' or extract_syllable(syl_1[2])[1] != '':
        return
    
    # Transpose the nucleus of the two syllables
    syllables[0] = syl_0[0] + syl_1[1] + syl_0[2]
    syllables[1] = syl_1[0] + syl_0[1] + syl_1[2]
    
    # Convert syllables to string
    new_syl  = util.syllables_to_text(syllables)
    new_word = util.syllables_to_word(syllables)
    
    return(new_word, new_syl)


'''
Desc: Batch for transpose_nucleus_word with a set of words
In  : data_train (pd.DataFrame)
Out : pd.DataFrame
'''
def transpose_nucleus(data_train, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT, stop=lambda: False):
    new_data = []

    for syl_word in data_train['syllables']:
        if stop():
            return
        
        transposed_word = transpose_nucleus_word(syl_word, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT)

        if transposed_word:
            new_data.append(transposed_word)
    
    # Convert to DataFrame and return it
    return pd.DataFrame(new_data, columns=['word', 'syllables'])


def acronym(data_train, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT, stop=lambda: False):
    # Check if a syllable only contains a single vowel
    def is_single_vowel(syl):
        syl_parts = extract_syllable(syl, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT)
        return syl_parts[0] == "" and syl_parts[2] == ""
    
    # Get list of syllable + new syllable from a syllabified text
    def get_syllable_list(syl_text):
        # Get the list of syllables
        syl_list = util.split_syllables(syl_text)

        # Remove duplicates
        syl_list = list(dict.fromkeys(syl_list))

        # Remove syllables that only contains a single vowel
        syl_list = list(filter(lambda x: not is_single_vowel(x), syl_list))

        # Augment new syllables
        new_syl = []

        for i in range(len(syl_list)-1):
            syl_parts_i = extract_syllable(syl_list[i], vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT)

            # Skip if the syllable has a coda (ending consonant)
            if syl_parts_i[2] != "":
                continue
            
            syl_parts_next = extract_syllable(syl_list[i+1], vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT)

            # Skip if the next syllable has no onset (leading consonant)
            if syl_parts_next[0] == "":
                continue
            
            # Make new syllable based on the current syllable and the next syllable
            new_syl.append(f"{syl_list[i]}{syl_parts_next[0]}")
        
        return syl_list + new_syl
    
    # Create a collection of syllable list of each word
    syl_list_collection = []
    
    for row in data_train.itertuples():
        syl_list_collection.append(get_syllable_list(row.syllables))
    
    # Augment new words
    df_new = pd.DataFrame([], columns=["word", "syllables"])

    for row_i in data_train.itertuples():        
        syl_list_i = syl_list_collection[row_i.Index]
        new_data_i = []
        
        for row_j in data_train.itertuples():
            if stop():
                return
            
            if row_i.Index == row_j.Index:
                continue

            syl_list_j = syl_list_collection[row_j.Index]

            for syl_i in syl_list_i:
                for syl_j in syl_list_j:
                    new_syl_list = [syl_i, syl_j] 
                    new_word = util.syllables_to_word(new_syl_list)
                    new_syl_text = util.syllables_to_text(new_syl_list)

                    new_data_i.append((new_word, new_syl_text))
        
        df_new_i = pd.DataFrame(new_data_i, columns=["word", "syllables"])
        df_new = pd.concat([df_new, df_new_i], ignore_index=True)
        df_new = df_new.drop_duplicates("syllables").reset_index(drop=True)

    return df_new


def validate_augmentation(data_train_aug, illegal_sequences, stop=lambda: False):
    new_data = []

    for row in data_train_aug.itertuples():
        if stop():
            return

        valid = True

        for seq in illegal_sequences["sequence"]:
            if seq in row.syllables:
                valid = False
                break
        
        if not valid:
            continue
            
        new_data.append((row.word, row.syllables))
    
    return pd.DataFrame(new_data, columns=['word', 'syllables'])

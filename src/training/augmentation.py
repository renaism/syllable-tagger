import src.utility as util
import pandas as pd

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
Desc: Generate new words by flipping the onset of the 1st and 2nd syllable
In  : data_train (pd.DataFrame)
Out : pd.DataFrame
'''
def flip_onsets(data_train):
    # List for storing new words
    new_data = []

    for syl_word in data_train['syllables']:
        # Convert syllable-segmented text to a list
        syllables = util.split_syllables(syl_word)
        
        # Skip if word only has one syllable
        if len(syllables) < 2:
            continue
        
        # Extract the 1st and 2nd syllables
        syl_0 = util.extract_syllable(syllables[0])
        syl_1 = util.extract_syllable(syllables[1])

        # Skip if one or both syllable doesn't have an onset
        if syl_0[0] == '' or syl_1[0] == '':
            pass
        
        # Flip the onset of the two syllables
        syllables[0] = syl_1[0] + syl_0[1] + syl_0[2]
        syllables[1] = syl_0[0] + syl_1[1] + syl_1[2]
        
        # Convert syllables to string
        new_syl  = util.syllables_to_text(syllables)
        new_word = util.syllables_to_word(syllables)
        
        new_data.append((new_word, new_syl))
    
    # Convert to DataFrame and return it
    return pd.DataFrame(new_data, columns=['word', 'syllables'])


'''
Desc: Generate new words by swapping consonants in the word with another consonant
In  : data_train (pd.DataFrame)
Out : pd.DataFrame
'''
def swap_consonants(data_train):
    new_data = []
    for syl_word in data_train['syllables']:
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
        for sm_row in swap_map:
            new_letters = letters[:]
            for i, swap in enumerate(sm_row):
                if swap == 1:
                    swapped_letter = new_letters[swap_pos[i]]
                    new_letters[swap_pos[i]] = CONSONANT_SWAP_MAP[swapped_letter]
            
            # Append consonant-swapped word to the new data
            new_syl = ''.join(new_letters)
            new_word = new_syl.replace('.', '')
            new_data.append((new_word, new_syl))
    
    # Convert to DataFrame and return it
    return pd.DataFrame(new_data, columns=['word', 'syllables'])
import re
import numpy as np
import time
import json

'''
Desc: Extract the onset, nucleus, and coda from a valid syllable
In  : syllable (str)
Out : tuple
'''
def extract_syllable(syllable):
    # Onset, consonant prefix
    ons = re.search(r'^[^aeiou]*', syllable)
    # Nucleus, vocal or diphtong
    nuc = re.search(r'[aeiou]+', syllable)
    # Coda, consonant suffix
    cod = re.search(r'[^aeiou]*$', syllable)
    
    return (ons.group(), nuc.group(), cod.group())


'''
Desc: Combine list of syllables into a single word
In  : syllables (List)
Out : str
'''
def syllables_to_word(syllables):
    word = ''

    for syl in syllables:
        word += syl
    
    return word


'''
Desc: Convert list of syllables to a syllable-segmented text
In  : syllables (List)
Out : string
'''
def syllables_to_text(syllables):
    syl_text = ''

    for i, syl in enumerate(syllables):
        syl_text += syl
        syl_text += '.' if i < len(syllables)-1 else ''
    
    return syl_text


'''
Desc: Split syllable-segmented text to a list of syllables
In  : syl_text (str)
Out : List 
'''
def split_syllables(syl_text):
    return syl_text.replace('-','.').rstrip('.').split('.')


'''
Desc: Convert a gram containing tags to a string (for saving n-gram to a file)
In  : tags (tuple)
Out : str
'''
def tags_to_str(tags):
    tags_str = ''

    for tag in tags:
        tags_str += tag + ' '
    
    return tags_str.rstrip(' ')


'''
Desc: Convert a string of tags to a tuple (for loading n-gram from a file)
In  : str
Out : Tuple
'''
def str_to_tags(tags_str):
    return tuple(tags_str.split())


'''
Desc: Convert tagging result into syllable-segmented word
In  : word (str), tag_sequence (list)
Out : str
'''
def tags_to_segmented_word(word, tag_sequence):
    segmented_word = ''
    j = 0
    N = len(word)

    for i in range(N):
        if word[i] == '-':
            segmented_word += word[i]
        else:
            segmented_word += word[i]

            if tag_sequence[j][1] == '*' and i < N-1 and word[i+1] != '-':
                segmented_word += '.'
            
            j += 1
        
    return segmented_word


'''
Desc: Log value of a probability
In  : prob (float)
Out : float
'''
def log_prob(prob):
    if prob <= 0:
        return -np.inf
    
    return np.log(prob)


'''
Desc: Print objects if the verbose flag is set to True
In  : verbose (bool), *args
'''
def printv(verbose, *args, end='\n'):
    if verbose:
        print(*args, end=end)


'''
Desc: Print each key and value of a dict
In  : data (dict)
'''
def print_dict(data, blank_line_after=True):
    for key, value in data.items():
        print('{}: {}'.format(key, value))
    
    if blank_line_after:
        print()


'''
Desc: Save dict to a log file
In: data (dict), fname (str)
'''
def save_dict_to_log(data, fname, folder='./'):
    timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    
    with open('{}{}_{}'.format(folder, timestamp, fname), mode='w') as f:
        f.write(json.dumps(data, indent=4))
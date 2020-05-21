import re
import numpy as np
import time
import json

class ContinuousPrint(object):
    def __init__(self, time_interval=1.0):
        self.time_interval = time_interval
        self.last_time = time.time() - time_interval


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
In  : verbose (bool), *args, end (char), cp (ContinuousPrint)
'''
def printv(verbose, *args, end='\n', cp=None):
    if not verbose:
        return
    
    if cp != None: 
        if time.time() < cp.last_time + cp.time_interval:
            return
        else:
            cp.last_time = time.time()

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
Desc: Get current date and time in formatted text
Out : str
'''
def get_current_timestamp():
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


'''
Desc: Save dict to a log file
In: data (dict), fdir (str)
Out: str
'''
def save_dict_to_log(data, fname, fdir='./'):
    timestamp = get_current_timestamp()
    fpath = f"{fdir}/{timestamp}_{fname}.log"
    
    with open(fpath, mode='w') as f:
        f.write(json.dumps(data, indent=4))
    
    return fpath
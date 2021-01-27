import utility as util
import pandas as pd
import re
import time
import multiprocessing

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


def acronym(data_train, fdir, batch=100, check_at=1000000, start_at=None, end_at=None, vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT, stop=lambda: False, verbose=False):        
    start_t = time.time()
    
    # Get list of syllable + new syllable from a syllabified text
    def get_syllable_list(syl_text):
        # Get the list of syllables
        syl_list = util.split_syllables(syl_text)

        # Remove duplicates
        syl_list = list(dict.fromkeys(syl_list))
        
        # Extract syllable parts from each syllable
        for i in range(len(syl_list)):
            syl_list[i] = extract_syllable(syl_list[i], vowels=VOWELS_DEFAULT, semi_vowels=SEMI_VOWELS_DEFAULT, diphtongs=DIPHTONGS_DEFAULT)

        # Augment new syllables
        new_syl = []

        for i in range(len(syl_list)):
            # If the syllable is an open syllable (ends with a vowel), add the onset from the next syllable (if any)
            if syl_list[i][2] == "" and i+1 < len(syl_list):                
                if syl_list[i+1][0] != "":
                    new_syl.append((syl_list[i][0], syl_list[i][1], syl_list[i+1][0][0]))

            # If the syllable is a closed syllable (ends with a consonant), remove the coda from the syllable
            elif syl_list[i][2] != "":
                new_syl.append((syl_list[i][0], syl_list[i][1], ""))
        
        syl_list += new_syl

        # Remove syllables that only contains a single vowel (no consonant)
        syl_list = list(filter(lambda x: x[0] != "" or x[2] != "", syl_list))
        
        return syl_list
    
    # Insert new word from the combination of two syllables to the list of new words (new_data) with duplicate checking each n-th iteration
    def inset_new_word(new_syl_text_list, syl_a, syl_b, batch_n):
        # If the 1st syllable is a closed syllable (ends with a consonant/has a coda) and the 2nd syllable has no onset,
        # move the coda from the 1st syllable to the 2nd syllable as an onset
        if syl_a[2] != "" and syl_b[0] == "":
            syl_a_text = f"{syl_a[0]}{syl_a[1]}"
            syl_b_text = f"{syl_a[2]}{syl_b[1]}{syl_b[2]}"
        else:
            syl_a_text = f"{syl_a[0]}{syl_a[1]}{syl_a[2]}"
            syl_b_text = f"{syl_b[0]}{syl_b[1]}{syl_b[2]}"

        new_syl_list = [syl_a_text, syl_b_text]
        new_syl_text = util.syllables_to_text(new_syl_list)
        new_syl_text_list.append(new_syl_text)
    
    def check_duplicate():
        nonlocal new_syl_text_list, c, checked, current_unique_pool, total_check_time

        check_start_t = time.time()
        new_syl_text_list = list(dict.fromkeys(new_syl_text_list))
        c = 0
        checked += 1
        current_unique_pool = len(new_syl_text_list)
        total_check_time += time.time() - check_start_t

    def save_current_batch(fpath):
        nonlocal new_syl_text_list

        new_df = pd.DataFrame(new_syl_text_list, columns=["syllables"])
        new_df.insert(loc=0, column="word", value=new_df["syllables"].apply(lambda x: x.replace(".", "")))
        new_df.to_csv(fpath, sep="\t", index=False, header=False)
    
    # Create a collection of syllable list of each word
    syl_list_collection = []
    
    for row in data_train.itertuples():
        syl_list_collection.append(get_syllable_list(row.syllables))
    
    # Augment new words
    cp = util.ContinuousPrint()
    new_syl_text_list = []
    batch_n = 0
    total_new_words = 0
    c = 0
    checked = 0
    current_unique_pool = 0
    total_check_time = 0

    batch_times = []
    start_batch_t = time.time()

    if not start_at and not end_at:
        i_range = range(len(syl_list_collection))
    else:
        i_range = range(start_at-1 if start_at else 0, end_at if end_at else len(syl_list_collection))

    for i in i_range:
        util.printv(verbose, f"Progress: {i+1}/{len(syl_list_collection)} | Batch: {batch_n} | Checked: {checked} | Current new words: {current_unique_pool} + {c} (Saved: {total_new_words}) | Total check time: {total_check_time:.2f}s | Time: {time.time() - start_t:.2f}s", end='\r', cp=cp)
        for j in range(i+1, len(syl_list_collection)):
            if stop():
                return

            for syl_i in syl_list_collection[i]:
                for syl_j in syl_list_collection[j]:
                    inset_new_word(new_syl_text_list, syl_i, syl_j, batch_n)
                    inset_new_word(new_syl_text_list, syl_j, syl_i, batch_n)
                    c += 2
            
                    if c >= check_at:
                        check_duplicate()
        
        if (i+1) % batch == 0 or i == i_range[-1]:
            check_duplicate()

            batch_n += 1
            save_current_batch(f"{fdir}/batch_{batch_n}.txt")
            total_new_words += len(new_syl_text_list)
            new_syl_text_list = []

            batch_times.append(time.time() - start_batch_t)
            start_batch_t = time.time()

    util.printv(verbose, f"Progress: {i+1}/{len(syl_list_collection)} | Batch: {batch_n} | Checked: {checked} | Current new words: {current_unique_pool} + {c} (Saved: {total_new_words}) | Total check time: {total_check_time:.2f}s | Time elapsed: {time.time() - start_t:.2f}s", end='\n')

    return {
        "total_new_words": total_new_words,
        "total_times": time.time() - start_t,
        "duplicate_check": checked,
        "batch": batch_n,
        "batch_times": batch_times
    }


def validate_augmentation_worker(proc_i, word_syllables, illegal_sequences):
    new_data = []
    print(f"{proc_i}: {len(word_syllables)}")

    for syl in word_syllables:
        valid = True

        for seq in illegal_sequences:
            if seq in syl:
                valid = False
                break
        
        if not valid:
            continue
            
        new_data.append(syl)
    
    return new_data


def validate_augmentation(data_train_aug, illegal_sequences, n_proc=1, stop=lambda: False):
    batch = len(data_train_aug) // n_proc
    word_syllables = list(data_train_aug["syllables"])
    ill_seq = list(illegal_sequences["sequence"])

    pool = multiprocessing.Pool(processes=n_proc)
    new_data_batch = pool.starmap(validate_augmentation_worker, [
        (i, word_syllables[i*batch : (i+1)*batch if i < n_proc-1 else len(data_train_aug)], ill_seq) for i in range(n_proc)
    ])

    new_data = []
    for i in range(len(new_data_batch)):
        print(f"{i}: {len(new_data_batch[i])}")
        new_data += new_data_batch[i]
    
    new_df = pd.DataFrame(new_data, columns=["syllables"])
    new_df.insert(loc=0, column="word", value=new_df["syllables"].apply(lambda x: x.replace(".", "")))
    
    return new_df

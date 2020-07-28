import time
import sys
import pandas as pd
import testing.tagger as tagger
import testing.probability as probability
import utility as util

from config import *


'''
Desc: Count the number of wrong syllables from the prediction compared to the true syllables
In  : pred_syl (list), truth_syl (list)
Out : int
'''
def mismatch_count(pred_syl, truth_syl):
    pred_n  = len(pred_syl)
    truth_n = len(truth_syl)
    
    i = 0
    j = 0
    count = 0
    start_i = 0

    for i in range(truth_n):
        j = 0
        s = 0

        while(s < start_i and j < pred_n-1):
            s += len(pred_syl[j])
            j += 1
        
        if truth_syl[i] != pred_syl[j]:
            count += 1
        
        start_i += len(truth_syl[i])
    
    return count


'''
Desc: Syllabify each word in the test set
In  : data_test (pd.DataFrame), n (int), prob_args (dict), args (dict)
Out : pd.DataFrame
'''
def syllabify(data_test, n, prob_args, state_elim=True, stemmer=None, mode="syl", g2p_map=None, validation=True, verbose=True):
    start_t = time.time()
    
    total_words = len(data_test)
    util.printv(verbose, f"Total words: {total_words}")

    # n-gram probability cache
    prob_args["cache"] = probability.generate_prob_cache(n)

    # GKN discount cache
    if prob_args["method"] == "gkn":
        prob_args["d_cache"] = probability.generate_gkn_discount_cache(n, prob_args["n_gram"], prob_args["d_ceil"])
    
    # Augmented n-gram probability cache
    if prob_args["with_aug"]:
        prob_args["cache_aug"] = probability.generate_prob_cache(n)

        # GKN discount cache
        if prob_args["method"] == "gkn":
            prob_args["d_cache_aug"] = probability.generate_gkn_discount_cache(n, prob_args["n_gram_aug"], prob_args["d_ceil"])

    wrong_words = 0
    total_syllables = 0
    wrong_syllables = 0
    syllable_error_rate = 0

    syl_preds = []
    mm_counts = []

    i = 0
    progress = 0

    cp = util.ContinuousPrint()

    for row in data_test.itertuples():
        i += 1

        # Tag the letters of the word
        tag_sequence = tagger.tag_word(row.word, n, prob_args, state_elim=state_elim, stemmer=stemmer, mode=mode, g2p_map=g2p_map)
        
        if mode == "syl":
            syl_pred = util.tags_to_segmented_word(row.word, tag_sequence)
        elif mode == "g2p":
            syl_pred = "".join(tag_sequence)
        
        syl_preds.append(syl_pred)

        # Compare the real and predicted syllables and count the differences
        mm_count = 0
        
        if validation:
            if mode == "syl":
                real_syllables = util.split_syllables(row.syllables)
            elif mode == "g2p":
                real_syllables = row.syllables.replace(".", "").replace("-", "")
            
            total_syllables += len(real_syllables)

            if row.syllables != syl_pred:
                wrong_words += 1
                
                if mode == "syl":
                    pred_syllables = util.split_syllables(syl_pred)
                elif mode == "g2p":
                    pred_syllables = syl_pred.replace(".", "").replace("-", "")
                
                mm_count = mismatch_count(pred_syllables, real_syllables)

                wrong_syllables += mm_count
        
            mm_counts.append(mm_count)
            syllable_error_rate = wrong_syllables / total_syllables
        
        progress = i / total_words

        output = 'Words tagged: {}/{} ({:.2f}%)'.format(i, total_words, progress * 100)
        output += ' | SER: {:.3f}%'.format(syllable_error_rate * 100)
        output += ' | Running time: {:.2f} s'.format(time.time() - start_t)
        if progress < 1:
            util.printv(verbose, output, end='\r', cp=cp)
        else:
            util.printv(verbose, output)
        
    word_error_rate = wrong_words / total_words

    data_result = data_test.copy()
    data_result['prediction'] = syl_preds

    if validation:
        data_result['mismatch_count'] = mm_counts
    
    end_t = time.time()

    return {
        'data': data_result,
        'metadata': {
            'total_words': total_words,
            'wrong_words': wrong_words,
            'correct_words': total_words - wrong_words,
            'word_error_rate': round(word_error_rate, 8),
            'total_syllables': total_syllables,
            'wrong_syllables': wrong_syllables,
            'correct_syllables': total_syllables - wrong_syllables,
            'syllable_error_rate': round(syllable_error_rate, 8),
            'start_time': time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime(start_t)),
            'end_time': time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime(end_t)),
            'duration': round(end_t - start_t, 2)
        }
    }


'''
Desc: Save syllabification result to a file
In  : result_data (pd.DataFrame), fpath (str)
'''
def save_result(result_data, fname, fdir, timestamp=True):
    fpath = f"{fdir}/"
    
    if timestamp:
        fpath += f"{util.get_current_timestamp()}_"
    
    fpath += f"{fname}.txt"
    
    result_data.to_csv(
        fpath, 
        sep='\t', 
        index=False,
        header=False
    )


'''
Desc: Load syllabification result from a file
In  : fpath (str)
Out : dict
'''
def load_result(fpath):
    columns = ['word', 'syllables', 'prediction', 'mismatch_count']
    data = pd.read_csv(fpath, sep='\t', header=None, names=columns, na_filter=False)
    
    total_words = len(data)
    wrong_words = 0
    total_syllables = 0
    wrong_syllables = 0

    for _, row in data.iterrows():
        real_syllables = util.split_syllables(row['syllables'])
        total_syllables += len(real_syllables)

        if row['mismatch_count'] > 0:
            wrong_words += 1
            wrong_syllables += row['mismatch_count']
    
    syllable_error_rate = wrong_syllables / total_syllables
    word_error_rate = wrong_words / total_words

    result = {
        'data': data,
        'metadata': {
            'total_words': total_words,
            'wrong_words': wrong_words,
            'correct_words': total_words - wrong_words,
            'word_error_rate': round(word_error_rate, 5),
            'total_syllables': total_syllables,
            'wrong_syllables': wrong_syllables,
            'correct_syllables': total_syllables - wrong_syllables,
            'syllable_error_rate': round(syllable_error_rate, 5),
        }
    }
    print('Successfully loaded "{}"'.format(fpath))
    
    return result


'''
Desc: Compare two result based on correctness of each result
In  : result1 (pd.DataFrame), result2 (pd.DataFrame), result1_wrong (bool), result2_wrong (bool)
Out : dict
'''
def compare_results(result1, result2, result1_wrong=True, result2_wrong=False):
    df = pd.merge(
        result1['data'], result2['data'],
        how='inner', on=['word', 'syllables'], suffixes=('_1', '_2')
    )

    return df[
        (((df['mismatch_count_1'] > 0) == result1_wrong) & ((df['mismatch_count_2'] > 0) == result2_wrong))
    ]
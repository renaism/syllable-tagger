import time
import sys
import pandas as pd
import numpy as np
import src.testing.tagger as tagger
import src.utility as util

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
def syllabify(data_test, n, prob_args, state_elim=True, validation=True, verbose=True):
    start_t = time.time()

    total_words = len(data_test)
    wrong_words = 0
    total_syllables = 0
    wrong_syllables = 0
    syllable_error_rate = 0

    syl_preds = []
    mm_counts = []

    i = 0
    progress = 0

    for row in data_test.itertuples():
        i += 1

        # Tag the letters of the word
        tag_sequence = tagger.tag_word(row.word, n, prob_args, state_elim=state_elim)
        syl_pred = util.tags_to_segmented_word(row.word, tag_sequence)
        syl_preds.append(syl_pred)

        # Compare the real and predicted syllables and count the differences
        mm_count = 0
        
        if validation:
            real_syllables = util.split_syllables(row.syllables)
            total_syllables += len(real_syllables)

            if row.syllables != syl_pred:
                wrong_words += 1
                pred_syllables = util.split_syllables(syl_pred)
                mm_count = mismatch_count(pred_syllables, real_syllables)
                wrong_syllables += mm_count
        
            mm_counts.append(mm_count)
            syllable_error_rate = wrong_syllables / total_syllables
        
        progress = i / total_words

        output = '\rWords tagged: {}/{} ({:.2f}%)'.format(i, total_words, progress * 100)
        output += ' | SER: {:.3f}%'.format(syllable_error_rate * 100)
        output += ' | Running time: {:.2f} s'.format(time.time() - start_t)
        util.printv(verbose, output, end='')
        
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
            'word_error_rate': round(word_error_rate, 5),
            'total_syllables': total_syllables,
            'wrong_syllables': wrong_syllables,
            'correct_syllables': total_syllables - wrong_syllables,
            'syllable_error_rate': round(syllable_error_rate, 5),
            'start_time': time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime(start_t)),
            'end_time': time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime(end_t)),
            'duration': round(end_t - start_t, 2)
        }
    }


'''
Desc: Save syllabification result to a file
In  : result_data (pd.DataFrame), fname (str), folder (str), with_timestamp (bool)
'''
def save_result(result_data, fname='', folder='./', with_timestamp=True):
    timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '_' if with_timestamp else ''
    path = '{}{}{}'.format(folder, timestamp, fname)

    result_data.to_csv(
        path, 
        sep='\t', 
        index=False, 
        header=False
    )


'''
Desc: Load syllabification result from a file
In  : fname (str), folder (str)
Out : dict
'''
def load_result(fname, folder='./'):
    columns = ['word', 'syllables', 'prediction', 'mismatch_count']
    data = pd.read_csv('{}{}'.format(folder, fname), sep='\t', header=None, names=columns, na_filter=False)
    
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
    print('Successfully loaded "{}"'.format(fname))
    
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
import pandas as pd
import time
import os
import re
import ngram
import utility as util

from training.preprocess import tokenize, pad_tokens
from training.augmentation import flip_onsets, swap_consonants, transpose_nucleus
from testing.syllabification import syllabify, save_result

from config import *

# Check if all filenames contain a suffix _fold_* and exclusive fold numbers
def get_folds_from_fnames(fnames):
    fold_list = []
    valid_folds = False
    
    for fn in fnames:
        fold_match = re.search(r"_fold_[0-9]+$", os.path.splitext(fn)[0])
        
        if fold_match != None:
            fold_i = int(fold_match.group()[6:])

            if fold_i not in fold_list:
                fold_list.append(fold_i)
            else:
                break
        else:
            break
    else:
        valid_folds = True
    
    if valid_folds:
        return fold_list
    else:
        None


def build_ngram(n_max, data_train_fnames, output_fname, output_fdir, lower_case=True, build_cont_fdist=True, build_follow_fdist=True):
    start_t = time.time()

    fold_list = get_folds_from_fnames(data_train_fnames)
    fold_mode = fold_list is not None

    print(f"Fold mode: {fold_mode}\n")

    for i in range(len(data_train_fnames)):
        idx = fold_list[i] if fold_mode else i+1

        if fold_mode:
            print(f"Fold {idx} ({i+1}/{len(fold_list)})")
        else:
            print(f"File {idx}/{len(data_train_fnames)}")
        
        print(f'Data train: "{data_train_fnames[i]}"')

        data_train = pd.read_csv(
            data_train_fnames[i],
            sep='\t',
            header=None,
            names=['word', 'syllables'],
            na_filter=False
        )

        # Lower case words
        if lower_case:
            data_train["word"] = data_train["word"].str.lower()
            data_train["syllables"] = data_train["syllables"].str.lower()

        # Build the n-gram
        tokens = pad_tokens(tokenize(data_train), n=n_max, start_pad=True, end_marker=True)
        ngram_fold = ngram.NGram(tokens, n=n_max, build_cont_fdist=build_cont_fdist, build_follow_fdist=build_follow_fdist, verbose=True)

        # Save the n-gram to a file
        fname = output_fname

        if fold_mode:
            fname += f"_fold_{idx}"
        elif len(data_train_fnames) > 1:
            fname += f"_{i+1}"
        
        ngram.save(ngram_fold, fname, output_fdir)
        print(f'n-gram saved to "{fname}"\n')
    
    print("DONE in {:.2f} s".format(time.time() - start_t))


def syllabify_folds(data_test_fnames, n_gram_fnames, n, prob_args, n_gram_aug_fnames=None, lower_case=True, output_fname=None, output_fdir=None, state_elim=True, validation=True, save_log=True, save_result_=True, timestamp=True):
    start_t = time.time()
    result_log = {
        "metadata": {
            "n_file": len(data_test_fnames),
            "n": n,
            "prob_args": prob_args.copy()
        },
        "overall": {},
        "results": {}
    }

    fold_list = get_folds_from_fnames(data_test_fnames)
    fold_mode = fold_list is not None
    
    print(f"Fold mode : {fold_mode}")
    print(f"State-elim: {state_elim}\n")

    if fold_mode:
        result_log["metadata"]["folds"] = str(fold_list)

    for i in range(len(data_test_fnames)):
        idx = fold_list[i] if fold_mode else i+1

        if fold_mode:
            print(f"Fold {idx} ({i+1}/{len(fold_list)})")
        else:
            print(f"File {idx}/{len(data_test_fnames)}")
        
        print(f'Data test: "{data_test_fnames[i]}"')

        data_test = pd.read_csv(
            data_test_fnames[i],
            sep='\t',
            header=None,
            names=['word', 'syllables'] if validation else ['word'],
            na_filter=False
        )

        # Lower case words
        if lower_case:
            data_test["word"] = data_test["word"].str.lower()
            if validation:
                data_test["syllables"] = data_test["syllables"].str.lower()

        print(f'n-gram model: "{n_gram_fnames[i]}"')

        prob_args["n_gram"] = ngram.load(
            n_gram_fnames[i], 
            n_max=n, 
            load_follow_fdist=True, 
            load_cont_fdist=True
        )

        if prob_args["with_aug"]:
            print(f'Aug n-gram model: "{n_gram_aug_fnames[i]}"')

            prob_args["n_gram_aug"] = ngram.load(
                n_gram_aug_fnames[i],
                n_max=n,
                load_follow_fdist=True, 
                load_cont_fdist=True
            )
    
        result = syllabify(data_test, n, prob_args, state_elim=state_elim, validation=validation)

        # Clear n_gram from memory
        prob_args['n_gram'] = None
        prob_args['n_gram_aug'] = None

        if save_log:
            result_log["results"][idx] = result["metadata"]
            result_log["results"][idx]["data_test"] = data_test_fnames[i]
            result_log["results"][idx]["n_gram"] = n_gram_fnames[i]

            if prob_args["with_aug"]:
                result_log["results"][idx]["n_gram_aug"] = n_gram_aug_fnames[i]
        
        if save_result_:
            fname = output_fname

            if fold_mode:
                fname += f"_fold_{idx}"
            elif len(data_test_fnames) > 1:
                fname += f"_{i+1}"

            save_result(result['data'], fname, output_fdir, timestamp=timestamp)

            print(f'Result saved to "{fname}"\n')
    
    end_t = time.time()

    if save_log:
        avg_ser = sum(result_log["results"][i]['syllable_error_rate'] for i in result_log["results"]) / (len(result_log["results"]))

        result_log['overall']['average_ser'] = round(avg_ser, 8)
        result_log['overall']['start_time'] = time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime(start_t))
        result_log['overall']['end_time'] = time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime(end_t))
        result_log['overall']['duration'] = round(end_t - start_t, 2)

        os.makedirs(f"{output_fdir}/logs", exist_ok=True)
        log_fpath = util.save_dict_to_log(result_log, f"log_{fname}", f"{output_fdir}/logs/")
        print(f'Log saved to "{log_fpath}"')
    
    print("DONE in {:.2f} s".format(end_t - start_t))


def augment_folds(data_train_fnames, output_fname, output_fdir, lower_case=True, flip_onsets_=False, swap_consonants_=False, transpose_nucleus_=False):
    start_t = time.time()

    fold_list = get_folds_from_fnames(data_train_fnames)
    fold_mode = fold_list is not None

    print(f"Fold mode: {fold_mode}\n")

    config = load_config()
    vowels = list(util.str_to_tags(config["SYMBOLS"]["vowels"]))
    semi_vowels = list(util.str_to_tags(config["SYMBOLS"]["semi_vowels"]))
    diphtongs = list(util.str_to_tags(config["SYMBOLS"]["diphtongs"]))

    for i in range(len(data_train_fnames)):
        idx = fold_list[i] if fold_mode else i+1

        if fold_mode:
            print(f"Fold {idx} ({i+1}/{len(fold_list)})")
        else:
            print(f"File {idx}/{len(data_train_fnames)}")
        
        print(f'Data train: "{data_train_fnames[i]}"')

        data_train = pd.read_csv(
            data_train_fnames[i],
            sep='\t',
            header=None,
            names=['word', 'syllables'],
            na_filter=False
        )

        # Lower case words
        if lower_case:
            data_train["word"] = data_train["word"].str.lower()
            data_train["syllables"] = data_train["syllables"].str.lower()

        # Do various augmentation methods
        data_stack = [data_train]

        if flip_onsets_:
            print("Flipping onsets...", end="\r")
            new_data = []

            for data in data_stack:
                new_data.append(flip_onsets(data, vowels=vowels, semi_vowels=semi_vowels, diphtongs=diphtongs))
            
            data_stack += new_data

            print("Flipping onsets DONE in {:.2f} s".format(time.time() - start_t))
        
        if swap_consonants_:
            print("Swapping consonants...", end="\r")
            new_data = []

            for data in data_stack:
                new_data.append(swap_consonants(data))
            
            data_stack += new_data

            print("Swapping consonants DONE in {:.2f} s".format(time.time() - start_t))
        
        if transpose_nucleus_:
            print("Transposing nucleus...", end="\r")
            new_data = []

            for data in data_stack:
                new_data.append(transpose_nucleus(data, vowels=vowels, semi_vowels=semi_vowels, diphtongs=diphtongs))
            
            data_stack += new_data

            print("Transposing nucleus DONE in {:.2f} s".format(time.time() - start_t))
        
        # Combine all augmented data
        data_train_aug = pd.concat(data_stack[1:], ignore_index=True)
        print(f"Augmented data train length: {len(data_train_aug)} words")

        # Save the n-gram to a file
        fname = output_fname

        if fold_mode:
            fname += f"_fold_{idx}"
        elif len(data_train_fnames) > 1:
            fname += f"_{i+1}"
        
        data_train_aug.to_csv(
            f"{output_fdir}/{fname}.txt", 
            sep="\t", 
            index=False, 
            header=False
        )

        print(f'Augmented data train saved to "{fname}"\n')
    
    print("DONE in {:.2f} s".format(time.time() - start_t))




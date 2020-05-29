import time
import numpy as np
import utility as util
import testing.probability as probability

from config import *
from training.augmentation import flip_onsets_word, transpose_nucleus_word

VOCAL_LETTERS = ['a', 'e', 'i', 'o', 'u']

'''
Desc: Generate possible states that used to tag a word
In  : word (str), state_length (int)
Out : list
'''
def generate_states(word, state_length):
    initial_state = tuple(STARTPAD for _ in range(state_length))
    states = [initial_state]
    
    prev_start_index = 0
    prev_end_index = 1
    n = len(word)

    for i in range(n):
        c = 0
        if i+1 > state_length:
            prev_start_index += 2**state_length // 2
        
        for j in range(prev_start_index, prev_end_index):
            if i == n-1 and word[i] == WORDEND:
                states.append(states[j][1:] + (word[i],))
            else:
                states.append(states[j][1:] + (word[i] + SYLMID,))
                states.append(states[j][1:] + (word[i] + SYLEND,))
                c += 2
        
        prev_start_index = prev_end_index
        prev_end_index += c

    return list(set(states))


def generate_possible_syllabifications(word):
    n = 2**len(word)

    # Create a binary syl mid(0)/end(1) map
    bin_format ='0{}b'.format(len(bin(n-1)[2:]))
    syl_map = []

    for i in range(n):
        bin_i = [int(x) for x in format(i, bin_format)]

        # Only insert binary that ends with 1 (syl end)
        if bin_i[-1] == 1:
            syl_map.append(bin_i)
    
    for sm_row in syl_map:
        tag_sequence = []

        for i, syl in enumerate(sm_row):
            tag = SYLMID if syl == 0 else SYLEND
            tag_sequence.append(f"{word[i]}{tag}")
        
        syl_word = util.tags_to_segmented_word(word, tag_sequence)

        print(syl_word)


'''
Desc: Eliminate states that contain undesirable tags combination
In  : states (list)
Out : list
'''
def eliminate_states(states):
    new_states = []

    for state in states:
        # The last symbol of a word is always a syllable end
        if len(state) >= 2 and state[-1] == WORDEND and state[-2][-1] != SYLEND:
            continue
        
        # Eliminate state that contains syllable structure of V!C!V! or V!C!V*
        if len(state) >= 3:
            flag = False
            skip = False

            for i in range(1, len(state)):
                if state[i][0] == STARTPAD or state[i-1][0] == STARTPAD or state[i][0] == WORDEND:
                    continue

                if not flag:
                    # Set flag if found occurence of V!C!
                    if state[i-1][0] in VOCAL_LETTERS and state[i-1][1] == SYLMID:
                        if state[i][0] not in VOCAL_LETTERS and state[i][1] == SYLMID: 
                            flag = True
                else:
                    # Reset flag if found C*
                    if state[i][0] not in VOCAL_LETTERS and state[i][1] == SYLEND:
                        flag = False
                    # Set to eliminate state if found V! or V* after V!C!
                    elif state[i][0] in VOCAL_LETTERS:
                        skip = True
                        break
            
            if skip:
                continue
        
        new_states.append(state)
    
    return new_states


'''
Desc: Tag each letter in a word based on wether it's before syllable boundary or not
In  : word (str), prob_args (dict), state_elim (bool), verbose (bool)
Out : list 
'''
def _tag_word(word, n, prob_args, state_elim=True, verbose=False):
    start_t = time.time()
    
    prob_args["word"] = word

    # Add end-marker to the word
    word += WORDEND
    T = len(word)

    # Generate possible states
    states = generate_states(word, n-1)

    #if "aug_prob_fl" in prob_args and prob_args["aug_prob_fl"]:
    #    pass

    # Eliminate invalid states
    if state_elim:
        states = eliminate_states(states)
    
    N = len(states)
    V = np.full((T, N), -np.inf)
    B = {}

    prob_calc = 0
    
    # Initial state, consists of padding tags STARTPAD
    initial_state = tuple(STARTPAD for _ in range(n-1))
    
    # Starting log probabilities
    symbol = word[0]
    util.printv(verbose, 'Current symbol:', symbol)
    traversed_states = set()
    prob_args["can_aug_prob"] = False

    for i, state in enumerate(states):
        # Skip the state if it's doesn't match with the initial state or current symbol
        if initial_state[1:] != state[:-1] or state[-1][0] != symbol:
            continue

        traversed_states.add(state)
        tags = (initial_state[0], ) + state
        tr_logprob = util.log_prob(probability.get_probability(tags, prob_args))
        prob_calc += 1

        util.printv(verbose, '[{}] {}->{} : {:.5f}'.format(i, initial_state, state, tr_logprob))
        V[0, i] = tr_logprob
        B[0, state] = None
    
    # Find the maximum log probabilities reaching each state at time t
    for t in range(1, T):
        symbol = word[t]
        util.printv(verbose, '\nCurrent symbol:', symbol)
        
        prev_states = traversed_states
        traversed_states = set()

        if t == n-1 and t < T-1 and "aug_prob" in prob_args and prob_args["aug_prob"]:
            prob_args["can_aug_prob"] = True
        else:
            prob_args["can_aug_prob"] = False
        
        for j, state in  enumerate(states):
            # Skip the state if the end tag doesn't match with the current symbol
            if state[-1][0] != symbol:
                continue
            
            best = (-np.inf, None)
            for i, prev_state in enumerate(states):
                # Skip if the prev_state not in the previously traversed states
                if prev_state not in prev_states:
                    continue

                # Skip if the last tag of prev_state doesn't match with the first tag of the current state
                if prev_state[1:] != state[:-1]:
                    continue

                traversed_states.add(state)
                tags = (prev_state[0], ) + state
                tr_logprob = util.log_prob(probability.get_probability(tags, prob_args))
                va = V[t-1, i] + tr_logprob
                prob_calc += 1

                util.printv(verbose, '[{}, {}] {}->{} : {:.5f} | Sum: {:.5f}'.format(i, j, prev_state, state, tr_logprob, va))
                
                if va >= best[0]:
                    best = (va, prev_state)
                
            V[t, j] = best[0]
            B[t, state] = best[1] #if best[1] != None else states[np.argmax(V[t-1])]
    
    util.printv(verbose, '\nTotal probability calculations:', prob_calc)

    # Find the biggest probability for final state
    best = None
    for i, state in enumerate(states):
        # Only search state from the traversed state in the last iteration
        if state not in traversed_states:
            continue
        
        val = V[T-1, i]
        if not best or val > best[0]:
            best = (val, state)
    
    # Backtrack to find the state sequence
    current = best[1]
    sequence = [current[-1]]

    util.printv(verbose, '\nBacktrack:')
    util.printv(verbose, '[{}] {}'.format(T, current))
    
    for t in range(T-1, 0, -1):
        current = B[t, current]
        sequence.append(current[-1])

        util.printv(verbose, '[{}] {}'.format(t, current))
    
    sequence.reverse()
    
    # Remove end marker tag from output
    sequence = sequence[:-1]
    
    util.printv(verbose, '\nFinished tagging word in {:.2f} s'.format(time.time() - start_t))

    return sequence


'''
Desc: Split word based on hyphen before tagging it
In  : word (str), prob_args (dict), state_elim (bool), verbose (bool)
Out : list 
'''
def tag_word(word, n, prob_args, state_elim=True, verbose=False):
    # Split the word if it has hyphen into sub-words
    sub_words = word.replace('-', ' ').split()
    
    # Tag each sub word separately
    sequence = []

    for sub_word in sub_words:
        sequence += _tag_word(sub_word, n, prob_args, state_elim, verbose)
    
    return sequence
import time
import numpy as np
import utility as util
import testing.probability as probability

from config import *
from training.augmentation import flip_onsets_word, transpose_nucleus_word

VOCAL_LETTERS = ['a', 'e', 'i', 'o', 'u']


'''
Desc: Check if state contains undesirable tags combination, thus is invalid (for SYL)
In  : state (tuple)
Out : bool
'''
def is_state_valid(state):
    # The last symbol of a word is always a syllable end
    if len(state) >= 2 and state[-1] == WORDEND and state[-2][-1] != SYLEND:
        return False
    
    # Eliminate state that contains syllable structure of V!C!V! or V!C!V*
    if len(state) >= 3:
        flag = False

        for i in range(1, len(state)):
            # Skip checking if current tag is a padding tag or word-end tag
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
                    return False
    
    return True


'''
Desc: Generate possible states that used to tag a word (for SYL)
In  : word (str), state_length (int), state_elim (bool)
Out : list
'''
def generate_states(word, state_length, state_elim=False):
    states = []

    initial_state = tuple(STARTPAD for _ in range(state_length))
    states.append([initial_state])

    n = len(word)

    for i in range(n):
        states_i = []
        traversed_prev_states = set()

        for state in states[len(states)-1]:
            if state[1:] in traversed_prev_states:
                continue
            else:
                traversed_prev_states.add(state[1:])
            
            new_states = []

            if word[i] == WORDEND:
                new_states.append(state[1:] + (word[i],))
            else:
                new_states.append(state[1:] + (word[i] + SYLMID,))
                new_states.append(state[1:] + (word[i] + SYLEND,))
                    
            for new_state in new_states:
                if not state_elim or is_state_valid(new_state):
                    states_i.append(new_state)
        
        states.append(states_i)
    
    return states


'''
Desc: Check if a phoneme is an impossible phoneme based on its position and adjacent letters in the word (for G2P)
In  : phoneme (str), word (str), i (int)
Out : bool
'''
def is_phoneme_valid(phoneme, word, i):
    check_r = i < len(word)-2
    check_l = i > 0

    if check_r:
        if word[i+1] != ".":
            r = word[i+1]
        else:
            r = word[i+2]

    if check_l:
        if word[i-1] != ".":
            l = word[i-1]
        else:
            l = word[i-2]

    if check_r and word[i] == "a" and r not in ["i", "y"]:
        if phoneme == "$":
            return False

    if check_r and word[i] == "a" and r not in ["u", "w"]:
        if phoneme == "@":
            return False
    
    if check_r and word[i] == "e" and r not in ["i", "y"]:
        if phoneme == "%":
            return False
    
    if check_r and word[i] == "e" and r not in ["a", "e", "i", "o", "u"]:
        if phoneme in ["2", "3"]:
            return False

    if check_l and word[i] == "g" and l != "n":
        if phoneme == "*":
            return False
    
    if check_l and word[i] == "i" and l not in ["a", "e", "o"]:
        if phoneme == "*":
            return False
    
    if check_r and word[i] == "i" and r not in ["a", "e", "o"]:
        if phoneme == "4":
            return False
    
    if check_r and word[i] == "k" and r != "h":
        if phoneme == "(":
            return False
    
    if check_r and word[i] == "n" and r not in ["c", "j", "s", "y"]:
        if phoneme == "+":
            return False
    
    if check_r and word[i] == "n" and r not in ["g", "k"]:
        if phoneme == ")":
            return False
    
    if check_r and word[i] == "o" and r not in ["i", "y"]:
        if phoneme == "^":
            return False
    
    if check_r and word[i] == "s" and r != "y":
        if phoneme == "~":
            return False
    
    if check_l and word[i] == "u" and l != "a":
        if phoneme == "*":
            return False
    
    if check_r and word[i] == "u" and r not in ["a", "e", "o"]:
        if phoneme == "6":
            return False
    
    if check_l and word[i] == "y" and l not in ["n", "s"]:
        if phoneme == "*":
            return False
    
    return True


'''
Desc: Generate possible states that used to tag a word (for G2P)
In  : word (str), state_length (int), g2p_map (dict), state_elim (bool), pre_phoneme (list)
Out : list
'''
def generate_states_g2p(word, state_length, g2p_map, state_elim=False, pre_phoneme=None):
    states = []

    initial_state = tuple(STARTPAD for _ in range(state_length))
    states.append([initial_state])

    n = len(word)

    for i in range(n):
        states_i = []
        traversed_prev_states = set()

        for state in states[len(states)-1]:
            if state[1:] in traversed_prev_states:
                continue
            else:
                traversed_prev_states.add(state[1:])
            
            if i < n-1 and pre_phoneme and pre_phoneme[i] != None:
                new_phonemes = pre_phoneme[i]
            elif word[i] in g2p_map:
                new_phonemes = g2p_map[word[i]]
            else:
                new_phonemes = [word[i]]
            
            for new_phoneme in new_phonemes:
                if not state_elim or (state_elim and is_phoneme_valid(new_phoneme, word, i)):
                    states_i.append(state[1:] + (new_phoneme,))
        
        states.append(states_i)

    return states


'''
Desc: Tag each letter in a word based on wether it's before syllable boundary or not
In  : word (str), prob_args (dict), state_elim (bool), mode (syl/g2p), verbose (bool)
Out : list 
'''
def _tag_word(word, n, prob_args, state_elim=True, mode="syl", g2p_map=None, pre_phoneme=None, verbose=False):    
    start_t = time.time()
    
    prob_args["word"] = word

    # Add end-marker to the word
    word += WORDEND
    T = len(word)

    # Generate possible states
    if mode == "syl":
        states = generate_states(word, n-1, state_elim=state_elim)
    elif mode == "g2p":
        states = generate_states_g2p(word, n-1, g2p_map, state_elim=state_elim, pre_phoneme=pre_phoneme)
    
    N = len(max(states, key=len))
    V = np.full((T, N), -np.inf)
    B = {}

    prob_calc = 0
    
    # Initial state, consists of padding tags STARTPAD
    initial_state = tuple(STARTPAD for _ in range(n-1))
    
    # Starting log probabilities
    symbol = word[0]
    util.printv(verbose, 'Current symbol:', symbol)
    prob_args["can_aug_prob"] = False

    for i, state in enumerate(states[1]):
        tags = (initial_state[0], ) + state
        tr_logprob = util.log_prob(probability.get_probability(tags, prob_args))

        if mode == "g2p":
            tr_logprob += util.log_prob(probability.get_emission_prob(word[0], state[-1], prob_args["n_gram"]))

        prob_calc += 1

        util.printv(verbose, '[{}] {}->{} : {:.5f}'.format(i, initial_state, state, tr_logprob))
        V[0, i] = tr_logprob
        B[0, state] = None
    
    # Find the maximum log probabilities reaching each state at time t
    for t in range(1, T):
        symbol = word[t]
        util.printv(verbose, '\nCurrent symbol:', symbol)

        if t == n-1 and t < T-1 and "aug_prob" in prob_args and prob_args["aug_prob"]:
            prob_args["can_aug_prob"] = True
        else:
            prob_args["can_aug_prob"] = False
        
        for j, state in enumerate(states[t+1]):
            best = (-np.inf, None)

            for i, prev_state in enumerate(states[t]):
                # Skip if the last tag of prev_state doesn't match with the first tag of the current state
                if prev_state[1:] != state[:-1]:
                    continue

                tags = (prev_state[0], ) + state
                tr_logprob = util.log_prob(probability.get_probability(tags, prob_args))

                if mode == "g2p" and word[t] != WORDEND:
                    tr_logprob += util.log_prob(probability.get_emission_prob(word[t], state[-1], prob_args["n_gram"]))
                
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
    for i, state in enumerate(states[T]):
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
def tag_word(word, n, prob_args, state_elim=True, mode="syl", g2p_map=None, stemmer=None, verbose=False):
    # Split the word if it has hyphen into sub-words
    sub_words = word.replace('-', ' ').split()
    
    # Tag each sub word separately
    sequence = []

    for i, sub_word in enumerate(sub_words):
        pre_phoneme = None
        
        if mode == "g2p" and stemmer:
            prefix, root, d_suffix, i_suffix = stemmer.getRoot(sub_word)
            prefix_p, d_suffix_p, i_suffix_p = stemmer.getAffixPhonemes(root, prefix, d_suffix, i_suffix)

            pre_phoneme = list(prefix_p) +  [None for _ in range(len(root))] + list(d_suffix_p) + list(i_suffix_p)
            
        sequence += _tag_word(sub_word, n, prob_args, state_elim, mode, g2p_map, pre_phoneme, verbose)

        if mode == "g2p" and (i < len(sub_words)-1 or word[-1] == "-"):
            sequence.append('-')
    
    return sequence
from nltk.util import ngrams
from nltk.probability import FreqDist
import src.utility as util
import json
import time

class NGram():
    def __init__(self, tokens=None, n=2, verbose=False):
        if tokens != None:
            self.generate(tokens, n, verbose)
    

    '''
    Desc: Initialize the n-gram
    In  : tokens(list), n (int)
    F.S.: NGram initialized with frequency and continuation frequency distributions of each nth-gram
    '''
    def generate(self, tokens, n=2, verbose=False):
        start_t = time.time()
        n_tokens = len(tokens)
        util.printv(verbose, 'Number of words: ', n_tokens)

        # Build frequency table from unigram to n-gram
        util.printv(verbose, '\nBuilding frequency distribution')
        self.n = n
        self.grams = {}
        self.fdist = {}

        for i in range(1, n+1):
            start_ti = time.time()
            self.fdist[i] = FreqDist()

            for j, word_tokens in enumerate(tokens):
                word_ngrams = ngrams(word_tokens, n=i)

                # Count the frequency of each gram
                for gram in word_ngrams:
                    self.fdist[i][gram] += 1
                
                util.printv(verbose, 'n: {}/{} | Words: {}/{}'.format(i, n, j, n_tokens), end='\r')

            self.grams[i] = list(self.fdist[i].keys())
            
            util.printv(verbose, 'n: {}/{} | DONE in {:.2f} s'.format(i, n, time.time() - start_ti))
        
        # Build continuation count table
        util.printv(verbose, '\nBuilding continuation frequency distribution')
        self.continuation_fdist = {}

        for i in range(1, n):
            start_ti = time.time()
            self.continuation_fdist[i] = FreqDist()
            len_fdist = self.fdist[i+1].B()

            for j, grams in enumerate(self.fdist[i+1]):
                self.continuation_fdist[i][grams[1:]] += 1

                util.printv(verbose, 'n: {}/{} | Grams: {}/{}'.format(i, n-1, j, len_fdist), end='\r')
            
            util.printv(verbose, 'n: {}/{} | DONE in {:.2f} s'.format(i, n-1, time.time() - start_ti))
        
        # Build follow count table
        util.printv(verbose, '\nBuilding follow frequency distribution')
        self.follow_fdist = {}

        for i in range(1, n):
            start_ti = time.time()
            self.follow_fdist[i] = FreqDist()
            len_fdist = self.fdist[i+1].B()

            for j, grams in enumerate(self.fdist[i+1]):
                self.follow_fdist[i][grams[:-1]] += 1

                util.printv(verbose, 'n: {}/{} | Grams: {}/{}'.format(i, n-1, j, len_fdist), end='\r')
            
            util.printv(verbose, 'n: {}/{} | DONE in {:.2f} s'.format(i, n-1, time.time() - start_ti))

        util.printv(verbose, '\nFinished building n-gram in {:.2f} s'.format(time.time() - start_t))
    

    '''
    Desc: Get maximum n size
    Out : int
    '''
    def N(self):
        return self.n
    

    '''
    Desc: Get all grams of the nth-gram
    In  : n (int)
    Out : List
    '''
    def get_grams(self, n=None):
        if n == None:
            n = self.n
        return sorted(self.grams[n])
    

    '''
    Desc: Get frequency distribution of the nth-gram
    In  : n (int)
    Out : nltk.FreqDist
    '''
    def get_fdist(self, n=None):
        if n == None:
            n = self.n
        return self.fdist[n]
    

    '''
    Desc: Get continuation frequency distribution of the nth-gram
    In  : n (int)
    Out : nltk.FreqDist
    '''
    def get_continuation_fdist(self, n=None):
        if n == None:
            n = self.n
        return self.continuation_fdist[n]


    '''
    Desc: Get follow frequency distribution of the nth-gram
    In  : n (int)
    Out : nltk.FreqDist
    '''
    def get_follow_fdist(self, n=None):
        if n == None:
            n = self.n
        return self.follow_fdist[n]


    '''
    Desc: Get the frequency of a gram
    In  : gram (tuple)
    Out : int
    '''
    def get_count(self, gram):
        n = len(gram)
        assert n <= self.n
        
        return self.fdist[n][gram]
    

    '''
    Desc: Get the continuation frequency of a gram
    In  : gram (tuple)
    Out : int
    '''
    def get_continuation_count(self, gram):
        n = len(gram)
        assert n < self.n
        
        return self.continuation_fdist[n][gram]
    
    
    '''
    Desc: Get the follow frequency of a gram
    In  : gram (tuple)
    Out : int
    '''
    def get_follow_count(self, gram):
        n = len(gram)
        assert n < self.n
        
        return self.follow_fdist[n][gram]


    '''
    Desc: Pretty print the frequency distribution of the nth-gram
    In  : n (int)
    '''
    def print_fdist(self, n=None):
        if n == None:
            n = self.n
        
        for gram, _ in self.fdist[n].most_common():
            print(gram, ': ', self.fdist[n][gram])


'''
Desc: Encode the n-gram to JSON and save it in a file
In  : ngram (NGram), fname (str)
F.S.: n-gram saved in a file
'''
def save(ngram, fname):
    data = {
        'N': ngram.n,
        'fdist': {},
        'continuation_fdist': {},
        'follow_fdist': {}
    }
    
    # Encode frequency distribution
    for i, fd in ngram.fdist.items():
        data['fdist'][i] = {}
        
        for k, v in fd.items():
            data['fdist'][i][util.tags_to_str(k)] = v
    
    # Encode continuation frequency distribution
    for i, cfd in ngram.continuation_fdist.items():
        data['continuation_fdist'][i] = {}

        for k, v in cfd.items():
            data['continuation_fdist'][i][util.tags_to_str(k)] = v
    
    # Encode follow frequency distribution
    for i, ffd in ngram.follow_fdist.items():
        data['follow_fdist'][i] = {}

        for k, v in ffd.items():
            data['follow_fdist'][i][util.tags_to_str(k)] = v
    
    # Write to file
    with open(fname, mode='w') as f:
        f.write(json.dumps(data))


'''
Desc: Load n-gram from a file and decode it
In  : fname (str), n_max (int), load_cont_fdist (bool), load_follow_fdist (bool)
Out : NGram
'''
def load(fname, n_max=None, load_cont_fdist=True, load_follow_fdist=True):
    with open(fname) as f:
        data = json.loads(f.read())

    # n_max denotes max nth-gram loaded
    if n_max == None:
        n_max = data['N']
    
    assert n_max <= data['N']

    ngram = NGram()
    ngram.n = n_max
    
    # Decode frequency distribution
    ngram.fdist = {}

    for i, fd in data['fdist'].items():
        i = int(i)
        
        if i > n_max:
            continue 

        ngram.fdist[i] = FreqDist()

        for k, v in fd.items():
            tags = util.str_to_tags(k)
            ngram.fdist[i][tags] = int(v)
    
    # Decode continuation frequency distribution
    if load_cont_fdist and 'continuation_fdist' in data:
        ngram.continuation_fdist = {}

        for i, cfd in data['continuation_fdist'].items():
            i = int(i)

            if i > n_max:
                continue 

            ngram.continuation_fdist[i] = FreqDist()

            for k, v in cfd.items():
                tags = util.str_to_tags(k)
                ngram.continuation_fdist[i][tags] = int(v)
    
    # Decode follow frequency distribution
    if load_follow_fdist and 'follow_fdist' in data:
        ngram.follow_fdist = {}

        for i, ffd in data['follow_fdist'].items():
            i = int(i)

            if i > n_max:
                continue 
            
            ngram.follow_fdist[i] = FreqDist()

            for k, v in ffd.items():
                tags = util.str_to_tags(k)
                ngram.follow_fdist[i][tags] = int(v)

    # Get all unique grams from fdist keys
    ngram.grams = {}

    for i in range(1, ngram.n+1):
        ngram.grams[i] = list(ngram.fdist[i].keys())
    
    return ngram
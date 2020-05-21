import json
import utility as util
from nltk.probability import FreqDist

'''
Desc: Get the probability of a tag sqeuence from an n-gram with kneser-ney smoothing
In  : tags (tuple), n_gram (NGram), d (float), highest_order (bool)
Out : float
'''
def kn(tags, n_gram, d=0.75, highest_order=True):
    n = len(tags)
    
    # For unigram
    if n == 1:
        return max(n_gram.get_continuation_count(tags), 1) / n_gram.get_fdist(2).B()
    
    # For bigram and higher
    tags_prec  = tags[:-1]
    count_prec = n_gram.get_count(tags_prec)
    
    if highest_order:
        # Raw count of tag sequence
        ckn      = n_gram.get_count(tags)
        ckn_prec = count_prec
    else:
        # Continuation count of tag sequence
        ckn      = n_gram.get_continuation_count(tags)
        ckn_prec = n_gram.get_continuation_count(tags_prec)
    
    if count_prec == 0:
        return kn(tags[1:], n_gram, d=d, highest_order=True)
    
    # Normalizing constant (lambda)
    L = (d / max(count_prec, 1)) * max(n_gram.get_follow_count(tags_prec), 1)
    
    # Main formula
    return (max(ckn-d, 0) / max(ckn_prec, 1)) + L * kn(tags[1:], n_gram, d=d, highest_order=False)


'''
Desc: Get follow count distribution of a tag sequence, used in gkn
In  : tags (tuple), n_gram (NGram), ceil (int)
Out : defaultdict
'''
def follow_count_dist(tags, n_gram, ceil=3):
    n = len(tags) + 1
    assert n <= n_gram.N()
    
    fdist = FreqDist()
    for grams in n_gram.get_fdist(n):
        if grams[:-1] == tags:
            fdist[grams[-1]] = n_gram.get_count(grams)
    fdist_c = fdist.r_Nr()
    fdist_c_keys = list(fdist_c.keys())

    for c in fdist_c_keys:
        if c > ceil:
            fdist_c[ceil] += fdist_c[c]
            del fdist_c[c]
    
    return fdist_c


'''
Desc: Cut-off follow count distribution with a max value (ceil)
In  : fdist (defaultdict), ceil (int)
Out : defaultdict
'''
def cut_follow_fdist(fdist, ceil):
    fdist = fdist.copy()
    frequencies = list(fdist.keys())

    for i in frequencies:
        if i > ceil:
            fdist[ceil] += fdist[i]
            del fdist[i]
    
    return fdist


'''
Desc: Calculate discount value used in gkn
In  : n_gram (NGram), n (int), c (int), ceil (int), highest_order (bool)
Out : float
'''
def gkn_discount(n_gram, n, c, ceil=3, highest_order=True):
    if c == 0:
        return 0
    
    if highest_order:
        c_freq = n_gram.get_fdist(n).r_Nr()
    else:
        c_freq = n_gram.get_continuation_fdist(n).r_Nr()
    
    c = min(c, ceil)
    d = c - (c+1) * (c_freq[c+1] / c_freq[c])*(c_freq[1] / (c_freq[1] + 2*c_freq[2]))
    
    return max(d, 0)


'''
Desc: Get the probability of a tag sqeuence from an n-gram with generalized kneser-ney smoothing
In  : tags (tuple), n_gram (NGram), d_ceil (int), w (int), cache (dict), d_cache (dict), highest_order (bool)
Out : float
'''
def gkn(tags, n_gram, d_ceil=3, w=1, cache=None, d_cache=None, highest_order=True):
    n = len(tags)
    
    # Key used to access cache
    ckey = 'top' if highest_order else 'low'
    
    # Attempt to get probability from cache
    if cache != None and tags in cache[ckey][n]:
        return cache[ckey][n][tags]
    
    # For unigram
    if n == 1:
        prob = max(n_gram.get_continuation_count(tags), 1) / n_gram.get_fdist(2).B()
    
    # For bigram and higher
    else:
        tags_prec  = tags[:-1]
        count      = n_gram.get_count(tags)
        count_prec = n_gram.get_count(tags_prec)

        # Constant to ensure the distribution sums to 1
        if count_prec > 0:
            #fc_dist = follow_count_dist(tags_prec, n_gram, ceil=d_ceil)
            fc_dist = cut_follow_fdist(n_gram.get_follow_fdist(tags_prec), ceil=d_ceil)

        # If context count is 0 or fc_dist is 0, back-off to lower order n-gram
        if count_prec == 0 or len(fc_dist.keys()) <= 1:
            return gkn(tags[1:], n_gram, d_ceil=d_ceil, w=w, cache=cache, d_cache=d_cache) 

        if highest_order:
            # Raw count of tag sequence
            ckn      = count
            ckn_prec = count_prec
        else:
            # Continuation count of tag sequence
            ckn      = n_gram.get_continuation_count(tags)
            ckn_prec = n_gram.get_continuation_count(tags_prec)

        # Discount
        if d_cache != None:
            D = d_cache[n][ckn] if ckn < d_ceil else d_cache[n][d_ceil]
        else:
            D = gkn_discount(n_gram, n, ckn, d_ceil, highest_order)


        gamma = 0
        for i in range(1, d_ceil+1):
            if d_cache != None:
                gamma += d_cache[n][i] * fc_dist[i] 
            else:
                gamma += gkn_discount(n_gram, n, i, d_ceil, highest_order) * fc_dist[i] 

        # Normalizing constant (lambda)
        L = gamma / count_prec

        # Main formula
        prob = (max(ckn-D, 0)/ckn_prec) + L*gkn(tags[1:], n_gram, d_ceil=d_ceil, w=w, cache=cache, d_cache=d_cache, highest_order=False) 
    
    weighted_prob = prob * w
    if cache != None:
        cache[ckey][n][tags] = weighted_prob

    return weighted_prob


'''
Desc: Get the probability of a tag sqeuence from an n-gram with stupid backoff smoothing
In  : tags (tuple), n_gram (NGram), alpha (float), cache (dict)
Out : float
'''
def stupid_backoff(tags, n_gram, alpha=0.4, cache=None):
    n = len(tags)

    # Check the cache if the probability of the tags already exists
    if cache != None and tags in cache['top'][n]:
        return cache['top'][n][tags]

    count = n_gram.get_count(tags)

    if count > 0 and n >= 2:
        tags_prec = tags[:-1]
        count_prec = n_gram.get_count(tags_prec)
        prob = count / count_prec
    elif n >= 2:
        prob = alpha * stupid_backoff(tags[1:], n_gram, alpha=alpha)
    else:
        # Unigram probability
        prob = n_gram.get_count(tags) / n_gram.get_fdist(1).N()
    
    # Store the probability to the cache
    if cache != None:
        cache['top'][n][tags] = prob
    
    return prob


'''
Desc: Get the probability of a tag sequence with specific arguments
In  : tags (tuple), args (dict), aug (bool)
Out : float
'''
def _get_probability(tags, args, aug=False):    
    # Assign n-gram
    if not aug:
        n_gram = args['n_gram']
    else:
        n_gram = args['n_gram_aug']

    w = args['aug_w'] if aug else 1

    # Assign caches
    cache = None

    if not aug and 'cache' in args:
        cache = args['cache']
    elif aug and 'cache_aug' in args:
        cache = args['cache_aug']

    # Call the corresponding probability/smoothing method
    if args['method'] == 'kn':
        return w * kn(tags, n_gram, args['d'])
    
    elif args['method'] == 'gkn':
        d_cache = None

        if not aug and 'd_cache' in args:
            d_cache = args['d_cache']
        elif aug and 'd_cache_aug' in args:
            d_cache = args['d_cache_aug']

        return gkn(tags, n_gram, d_ceil=args['d_ceil'], cache=cache, w=w, d_cache=d_cache)
    
    elif args['method'] == 'stupid_backoff':
        return w * stupid_backoff(tags, n_gram, args['alpha'], cache=cache)
        

'''
Desc: Wrapper for _get_probability function
In  : tags (tuple), args (dict)
Out : float
'''
def get_probability(tags, args):
    prob = _get_probability(tags, args)
    
    if 'with_aug' in args and args['with_aug']:
        prob += _get_probability(tags, args, aug=True)

    return prob


'''
Desc: Initialize a probability cache
In  : n (int)
Out : dict
'''
def generate_prob_cache(n):
    return {
        'top': {i: {} for i in range(1, n+1)},
        'low': {i: {} for i in range(1, n+1)} 
    }


'''
Desc: Initialize a discount cache
In  : n (int), n_gram (NGram), ceil (int)
Out : dict
'''
def generate_gkn_discount_cache(n, n_gram, ceil):
    d_cache = {}

    for i in range(2, n+1):
        d_cache[i] = {}

        for c in range(0, ceil+1):
            d_cache[i][c] = gkn_discount(n_gram, i, c, ceil=ceil, highest_order=i==n)
    
    return d_cache


'''
Desc: Save a probability cache to a file
In  : cache (dict), fname (str), folder (str)
'''
def save_cache(cache, fname, folder='./'):
    data = {}
    
    # Access top and low level of the cache
    for level in cache:
        data[level] = {}

        # Access each nth-gram order of the cache
        for i in cache[level]:
            data[level][i] = {}

            # Access each gram item of the cache
            for k, v in cache[level][i].items():
                data[level][i][util.tags_to_str(k)] = v 
    
    with open('{}{}'.format(folder, fname), mode='w') as f:
        f.write(json.dumps(data))


'''
Desc: Load a probability cache from a file
In  : fname (str), folder (str)
Out : dict
'''
def load_cache(fname, folder='./'):
    with open('{}{}'.format(folder, fname)) as f:
        data = json.loads(f.read())
    
    cache = {}

    # Access top and low level of the data
    for level in data:
        cache[level] = {}

        # Access each nth-gram order of the data
        for i, data_i in data[level].items():
            i = int(i)
            cache[level][i] = {}

            # Access each gram item of the data
            for k, v in data_i.items():
                cache[level][i][util.str_to_tags(k)] = float(v)
    
    return cache
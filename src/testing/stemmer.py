import os

class Stemmer:

    def __init__(self):
        self.dictionary = self.loadDictionary()

        self.i_suffix_phonemes = {
            '': '',
            '.kah': '.kah', 
            '.lah': '.lah', 
            '.tah': '.tah', 
            '.pun': '.pun',
            '.nya': '.+*a',
            '.ku': '.ku',
            '.mu': '.mu'
        }

        self.d_suffix_phonemes = {
            '': '',
            '.kan': '.kan',
            '.an': '.an',
            '.i': '.i'
        }

        self.prefix_phonemes = {
            '': '',
            'meng.': 'm#)*.', 
            'me.ng': 'm#.)*', 
            'meny.': 'm#+*.', 
            'me.ny': 'm#.+*',
            'ber.': 'b#r.', 
            'ter.': 't#r.', 
            'mem.': 'm#m.',
            'men.': 'm#n.', 
            'per.': 'p#r.', 
            'pem.': 'p#m.',
            'pen.': 'p#n.',
            'di.': 'di.', 
            'ke.': 'k#.', 
            'se.': 's#.', 
            'be.': 'b#.', 
            'te.': 't#.', 
            'me.': 'm#.', 
            'pe.': 'p#.'
        }

    def getRoot(self, word, check_prefix=True, check_d_suffix=True, check_i_suffix=True):
        prefix, d_suffix, i_suffix = '', '', ''
        root = word

        if check_i_suffix and not self.inDictionary(root.replace('.', '')):
            root, i_suffix = self.removeInflectionalSuffix(root)

        if check_d_suffix and not self.inDictionary(root.replace('.', '')):
            root, d_suffix = self.removeDerivationalSuffix(root)

        if check_prefix and not (self.inDictionary(root.replace('.', '')) or self.isInvalidAffixPair(word)):
            prefix, root = self.removePrefix(root)
        
        return prefix, root, d_suffix, i_suffix

    def loadDictionary(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        dictionaryFile = current_dir + '/kata-dasar.txt'
        root = ''
        with open(dictionaryFile, 'r') as f:
            root = f.read()
        return root.split('\n')

    def inDictionary(self, word):
        return word in self.dictionary

    def removeInflectionalSuffix(self, word):
        root = word
        i_suffix = ''

        if word.endswith(('.kah', '.lah', '.tah', '.pun', '.nya')) :
            root = word[:-4]
            i_suffix = word[-4:]
        elif word.endswith(('.ku','.mu')):
            root = word[:-3]
            i_suffix = word[-3:]
        
        return root, i_suffix

    def removeDerivationalSuffix(self, word):
        root = word
        d_suffix = ''
        
        if word.endswith('.kan'):
            root = word[:-4]
            d_suffix = word[-4:]
        elif word.endswith('.an'):
            root = word[:-3]
            d_suffix = word[-3:]
        elif word.endswith('.i'):
            root = word[:-2]
            d_suffix = word[-2:]
        
        return root, d_suffix

    def isInvalidAffixPair(self, word):
        tipe1 = word.startswith('be') and word.endswith('i')
        tipe2 = word.startswith('di') and word.endswith('an')
        tipe3 = word.startswith('ke') and (word.endswith('i') or word.endswith('kan'))
        tipe4 = word.startswith('me') and word.endswith('an')
        tipe5 = word.startswith('se') and (word.endswith('i') or word.endswith('kan'))
        tipe6 = word.startswith('te') and word.endswith('an')

        return (tipe1 or tipe2 or tipe3 or tipe4 or tipe5 or tipe6)

    def removePrefix(self, word):
        prefix = ''
        root = word

        if word.startswith(('meng.', 'me.ng', 'meny.', 'me.ny')):
            prefix = word[:5]
            root = word[5:]
        elif word.startswith(('ber.', 'ter.', 'mem.', 'men.', 'per.', 'pem.', 'pen.')):
            prefix = word[:4]
            root = word[4:]
        elif word.startswith(('di.', 'ke.', 'se.', 'be.', 'te.', 'me.', 'pe.')):
            prefix = word[:3]
            root = word[3:]

        return prefix, root
    
    def getAffixPhonemes(self, root, prefix='', d_suffix='', i_suffix=''):
        prefix_p = self.prefix_phonemes[prefix]
        d_suffix_p = self.d_suffix_phonemes[d_suffix]
        i_suffix_p = self.i_suffix_phonemes[i_suffix]

        if prefix_p.endswith('n.') and root[0] in ['c', 'j']:
            prefix_p = prefix_p.replace('n', '+')
        
        elif prefix_p.endswith('#.') and root[0] in ['a', 'e', 'i', 'o', 'u']:
            prefix_p = prefix_p.replace('#', '3')

        return prefix_p, d_suffix_p, i_suffix_p 
        

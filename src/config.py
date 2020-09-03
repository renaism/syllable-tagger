import os.path
import configparser
import utility as util

# Symbols for tag
SYLMID   = u"\u00A1" # Inverted Exclamation Mark - For letters that are not syllable boundary 
SYLEND   = u"\u2022" # Bullet - For letters that are syllable boundary
WORDEND  = u"\u00D7" # Multiplication Sign - For word ending
SYLBOUND = "." # Syllable boundary
STARTPAD = u"\u2205" # Pad for the beginning of each word

CONFIG_FNAME = "config.ini"

VOWELS_DEFAULT = ["a", "e", "i", "o", "u"]
SEMI_VOWELS_DEFAULT = ["y", "w"]
DIPHTONGS_DEFAULT = ["ai", "au", "ei", "oi", "ay", "aw", "ey", "oy"]

G2P_DEFAULT = {
    'a': ['a', '$', '@', '1'],
    'b': ['b'],
    'c': ['c'],
    'd': ['d'],
    'e': ['e', '#', '%', '2', '3'],
    'f': ['f'],
    'g': ['g', '*'],
    'h': ['h', '*'],
    'i': ['i', '*', '4'],
    'j': ['j'],
    'k': ['k', '(', '*'],
    'l': ['l'],
    'm': ['m'],
    'n': ['n', ')', '+'],
    'o': ['o', '^', '5'],
    'p': ['p'],
    'q': ['k'],
    'r': ['r'],
    's': ['s', '~'],
    't': ['t'],
    'u': ['u', '*', '6'],
    'v': ['f'],
    'w': ['w'],
    'x': ['s'],
    'y': ['y', '*'],
    'z': ['z'],
    SYLBOUND: [SYLBOUND],
    WORDEND: [WORDEND]
}


def init_config():
    config = configparser.ConfigParser( 
        converters={"list": lambda x: list(util.str_to_tags(x))}
    )

    return config


def create_config():
    config = init_config()

    config["DIRECTORIES"] = {
        "aug": "",
        "train": "",
        "test": ""
    }
    config["SYMBOLS"] = {
        "vowels": util.tags_to_str(VOWELS_DEFAULT),
        "semi_vowels": util.tags_to_str(SEMI_VOWELS_DEFAULT),
        "diphtongs": util.tags_to_str(DIPHTONGS_DEFAULT)
    }

    config["G2P"] = {}

    for g, p in G2P_DEFAULT.items():
        config["G2P"][g] = util.tags_to_str(p)

    return config


def save_config(config):
    with open(CONFIG_FNAME, "w", encoding='utf-8') as configfile:
        config.write(configfile)


def load_config():
    if os.path.isfile(CONFIG_FNAME):
        config = init_config()
        config.read(CONFIG_FNAME)
    else:
        config = create_config()
    
    return config


def get_config(section, key):
    config = load_config()

    return config[section][key]


def update_config(section, key, value):
    config = load_config()

    # Convert list to string
    if tpye(value) == list:
        value = util.tags_to_str(value)

    config[section][key] = value
    save_config(config)

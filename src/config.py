import os.path
import configparser
import utility as util

# Symbols for tag
SYLMID  = u"\u00A1" # Inverted Exclamation Mark - For letters that are not syllable boundary 
SYLEND  = u"\u2022" # Bullet - For letters that are syllable boundary
WORDEND = u"\u00D7" # Multiplication Sign - For word ending

STARTPAD = "#" # Pad for the beginning of each word

CONFIG_FNAME = "config.ini"

VOWELS_DEFAULT = ["a", "e", "i", "o", "u"]
SEMI_VOWELS_DEFAULT = ["y", "w"]
DIPHTONGS_DEFAULT = ["ai", "au", "aw", "ay", "ei", "ey", "oi", "oy"]

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

    return config


def save_config(config):
    with open(CONFIG_FNAME, "w") as configfile:
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

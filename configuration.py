import json
import os
import sys

SCRIPTDIR = os.path.dirname(os.path.realpath(sys.argv[0]))
#CONFIGPATH = os.path.join(SCRIPTDIR,'config.json')
CONFIGPATH ='/Users/trevor/PycharmProjects/buckeye/config.json'


def load_config():
    with open(CONFIGPATH, encoding='utf-8') as config_json:
        config = json.load(config_json)
        return config

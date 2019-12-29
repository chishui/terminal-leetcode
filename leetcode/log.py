import os
import json
import logging
import logging.config

json_file = os.path.join(os.path.expanduser('~'), '.config', 'leetcode', 'logging.json')


def read_json_data(filepath):
    with open(json_file, 'r') as f:
        return json.load(f)


def init_logger():
    if os.path.exists(json_file):
        logging.config.dictConfig(read_json_data(json_file))
    else:
        logging.basicConfig(level=logging.ERROR)

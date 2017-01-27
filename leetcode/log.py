import os
import json
import logging
import logging.config

json_file = os.path.join(os.path.expanduser('~'), '.config', 'leetcode', 'logging.json')
def init_logger():
    if os.path.exists(json_file):
        with open(json_file, 'rt') as f:
            data = json.load(f)
        logging.config.dictConfig(data)
    else:
        logging.basicConfig(level=logging.info)

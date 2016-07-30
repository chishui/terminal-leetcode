import os
from functools import wraps
from .config import CONFIG_FOLDER

SNIPPET_FOLDER = os.path.join(CONFIG_FOLDER, 'snippet')
BEFORE = os.path.join(SNIPPET_FOLDER, 'before')
AFTER = os.path.join(SNIPPET_FOLDER, 'after')

def get_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return ''

def enhance_code(func):
    @wraps(func)
    def wrapper(code, language, filepath):
        before = get_data(BEFORE)
        after = get_data(AFTER)
        code = before + code + after
        return func(code, language, filepath)
    return wrapper

def generate_makefile(func):
    @wraps(func)
    def wrapper(code, language, filepath):
        if language != 'C++':
            return func(code, language, filepath)
        directory = os.path.dirname(filepath)
        filename = os.path.split(filepath)[-1]
        name = filename.split('.')[0]
        makefile = os.path.join(directory, 'Makefile')
        text = 'all: %s\n\t g++ -g -o %s %s -std=c++11' % (filename, name, filename)
        with open(makefile, 'w') as f:
            f.write(text)
        return func(code, language, filepath)
    return wrapper

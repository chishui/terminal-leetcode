import os
from pathlib import Path
from functools import wraps
from .config import CONFIG_FOLDER, config
from .trace import trace
import subprocess

SNIPPET_FOLDER = os.path.join(CONFIG_FOLDER, 'snippet')
BEFORE = os.path.join(SNIPPET_FOLDER, 'before')
AFTER = os.path.join(SNIPPET_FOLDER, 'after')

@trace
def get_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return ''

@trace
def enhance_code(func):
    @wraps(func)
    def wrapper(code, language, filepath):
        before = get_data(BEFORE)
        after = get_data(AFTER)
        code = before + code + after
        return func(code, language, filepath)
    return wrapper

@trace
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

#def write_quiz_detail(data, f):
    #lines = data.body.split('\n')
    #f.write('/*\n')
    #comment_symbol = "* "
    #for line in lines:
        #f.write(comment_symbol)
        #f.write(line.encode('utf8') + '\n')
    #f.write('*/\n')

@trace
def unique_file_name(filepath):
    if not os.path.exists(filepath):
        return filepath

    path, ext = os.path.splitext(filepath)
    path, filename = os.path.split(path)
    index = 1
    while os.path.exists(filepath):
        filepath =  os.path.join(path, filename + '-' + str(index) + ext)
        index = index + 1
    return filepath

@trace
def get_code_file_path(quiz_id):
    path = config.path
    if not path or not Path(config.path).exists():
        path = Path.home() / 'leetcode'
        if not path.exists():
            path.mkdir()
    else:
        path = Path(path)

    return path / Path(str(quiz_id) + '.' + config.ext)

@trace
def get_code_for_submission(filepath):
    data = get_data(filepath)
    before = get_data(BEFORE)
    after = get_data(AFTER)
    return data.replace(before, '').replace(after, '')

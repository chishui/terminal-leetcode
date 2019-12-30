from pathlib import Path
from functools import wraps
from ..helper.config import CONFIG_FOLDER, config
from ..helper.trace import trace

SNIPPET_FOLDER = Path(CONFIG_FOLDER) / Path('snippet')
BEFORE = SNIPPET_FOLDER.joinpath('before')
AFTER = SNIPPET_FOLDER.joinpath('after')


@trace
def get_data(filepath):
    if filepath.exists():
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
        directory = filepath.parent
        filename = filepath.name
        name = filepath.stem
        makefile = directory.joinpath('Makefile')
        text = 'all: %s\n\t g++ -g -o %s %s -std=c++11' % (filename, name, filename)
        with open(makefile, 'w') as f:
            f.write(text)
        return func(code, language, filepath)
    return wrapper


@trace
def unique_file_name(filepath):
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if not filepath.exists():
        return filepath

    path = filepath.parent
    filename = filepath.stem
    ext = filepath.suffix
    index = 1
    while filepath.exists():
        filepath = path / Path(filename + '-' + str(index) + ext)
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


@trace
def edit_code(quiz_id, code, newcode=False):
    filepath = get_code_file_path(quiz_id)
    if newcode:
        filepath = unique_file_name(filepath)

    code = prepare_code(code, config.language, filepath)
    if not filepath.exists():
        with open(filepath, 'w') as f:
            f.write(code)
    return filepath


@enhance_code
@generate_makefile
def prepare_code(code, language, filepath):
    return code

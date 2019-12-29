import argparse
from .common import LANG_MAPPING
from .config import config
from .__main__ import main as main_entry


def main():
    parser = argparse.ArgumentParser(prog='Terminal Leetcode', description='Terminal Leetcode')
    parser.add_argument('setting', nargs='?', help='Set configuration')
    parser.add_argument('-l', '--language', action='store', choices=LANG_MAPPING.keys(),
                        help='Set programming language')
    parser.add_argument('-p', '--path', action='store', help='Set programming file location')
    parser.add_argument('-e', '--ext', action='store', help='Set programming file extention')

    args = parser.parse_args()
    if args.setting:
        if args.setting == "setting":
            if args.language:
                config.write('language', args.language)
            elif args.ext:
                config.write('ext', args.ext)
            elif args.path:
                config.write('path', args.path)
        else:
            parser.print_help()
    else:
        main_entry()

import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as fh:
    long_description = fh.read()


requirements = ['urwid', 'requests', 'bs4', 'lxml', 'decorator', 'pycookiecheat']

setup(
    name="terminal-leetcode",
    version="0.0.18",
    author="Liyun Xiu",
    author_email="chishui2@gmail.com",
    description="A terminal based leetcode website viewer",
    license="MIT",
    keywords="leetcode terminal urwid",
    url="https://github.com/chishui/terminal-leetcode",
    packages=['leetcode', 'leetcode/views', 'leetcode/client',
        'leetcode/coding', 'leetcode/helper'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    entry_points={'console_scripts': ['leetcode=leetcode.cli:main']},
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console :: Curses",
        "Topic :: Utilities",
        "Topic :: Terminals",
        "License :: OSI Approved :: MIT License",
    ]
)

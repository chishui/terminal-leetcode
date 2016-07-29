============================
Terminal-Leetcode
============================
Terminal-Leetcode is a terminal based leetcode website viewer.  
This project is inspired by RTV.

![alt text](screenshots/list.gif "quiz list" )
<!--![alt text](screenshots/detail.png "quiz detail")-->
---------------

[![Build Status](https://travis-ci.org/chishui/terminal-leetcode.svg?branch=master)](https://travis-ci.org/chishui/terminal-leetcode)
[![PyPI](https://img.shields.io/pypi/v/nine.svg?maxAge=2592000)](https://pypi.python.org/pypi/terminal-leetcode)
[![PyPI](https://img.shields.io/badge/python-2.7-blue.svg?maxAge=2592000)](https://pypi.python.org/pypi/terminal-leetcode)

---------------
# Requirements
- Python 2.7  
- [Urwid](https://github.com/urwid/urwid)

# Installation
Install with pip  
```
 $ pip install terminal-leetcode
```
Clone the repository  
```
 $ git clone https://github.com/chishui/terminal-leetcode.git  
 $ cd terminal-leetcode  
 $ sudo python setup.py install  
```
# Usage
To run the program, input leetcode in terminal    
```
 $ leetcode
```
### Login
To login you need to create a config.cfg file in folder ~/.config/leetcode.  
Input your username and password in config.cfg as:  
```
[leetcode]
username=chishui
password=123456
```
Then restart this program.
### Program Language
You can set your program language in config.cfg as:
```
[leetcode]
........
language=Java
```
to see default sample code in quiz detail view in your favorate language.  
Please make sure to use Leetcode support program languages and use the string exactly 
the same as it appears in Leetcode.    
Default language is C++.
### Writing Code
Terminal-Leetcode allows you to open editor to edit quiz default code you are viewing.  
You can set your code editing settings in config.cfg as:
```
[leetcode]
........
ext=java # file extention
path=~/program/leetcode # code file directory
```
Then when you are in quiz detail view, press ``e`` to open editor to edit code sample.  
Code sample is saved into directory you set in config.cfg automatically with file name combined
with quiz id and file extention you set.  
Default editor is vim, you can set ``export EDITOR=***`` to change editor. You can refer to
[this article](http://sweetme.at/2013/09/03/how-to-open-a-file-in-sublime-text-2-or-3-from-the-command-line-on-mac-osx/)
to use Sublime Text as command line editor.



# Controls:
- Press ``H`` to see help infomation.  
- Press ``up`` and ``down`` to go through quiz list.  
- Press ``enter`` or ``right`` to see a quiz detail, and press ``left`` to go back.  
- Press ``R`` in quiz list view to retrieve quiz from website.  
- Press ``PageUp`` or ``PageDown`` to go to prev or next page.  
- Press ``f`` to search quiz by id.
- Press ``e`` to open editor to edit code.
- Press ``1`` to sort quiz list by id.
- Press ``2`` to sort quiz list by title.
- Press ``3`` to sort quiz list by acceptance.
- Press ``4`` to sort quiz list by difficulty.  
Vim's moving keys ``h``, ``j``, ``k``, ``l``, ``ctrl+f``, ``ctrl+b`` are supported.



# TODO
- Test
- ~~User login~~
- ~~Quiz list sort~~
- ~~Install with pip~~
- ~~Get quiz default code interface~~

# Contribute
All kinds of contributions are welcome.

# Licence
MIT


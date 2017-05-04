import os
import subprocess
from views.viewhelper import *
from .config import config

def edit(filepath, loop):
    editor = os.environ.get('EDITOR', 'vi').lower()
    # vim
    if editor == 'vi' or editor == 'vim':
        cmd = editor + ' ' + filepath
        current_directory = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(filepath)))
        if config.tmux_support and is_inside_tmux():
            open_in_new_tmux_window(cmd)
        else:
            subprocess.call(cmd, shell=True)
            delay_refresh_detail(loop)
        os.chdir(current_directory)
    # sublime text
    elif editor == 'sublime':
        cmd = 'subl ' + filepath
        subprocess.call(cmd, shell=True)

def is_inside_tmux():
    return 'TMUX' in os.environ

def open_in_new_tmux_window(edit_cmd):
    # close other panes if exist, so that the detail pane is the only pane
    try:
        output = subprocess.check_output("tmux list-panes | wc -l", shell=True)
        num_pane = int(output)
        if num_pane > 1:
            subprocess.check_call("tmux kill-pane -a", shell=True)
    except:
        pass
    cmd = "tmux split-window -h"
    os.system(cmd)
    cmd = "tmux send-keys '%s' C-m" % edit_cmd
    os.system(cmd)

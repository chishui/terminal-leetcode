def refresh(loop, data):
    loop.draw_screen()


def delay_refresh(loop):
    alarm = loop.set_alarm_in(1, refresh)
    return alarm


def refresh_detail(loop, data):
    loop.screen.clear()
    loop.draw_screen()


def delay_refresh_detail(loop):
    alarm = loop.set_alarm_in(1, refresh_detail)
    return alarm


def vim_key_map(key):
    if key == 'j':
        return 'down'
    elif key == 'k':
        return 'up'
    elif key == 'h':
        return 'left'
    elif key == 'l':
        return 'right'
    elif key == 'ctrl f':
        return 'page down'
    elif key == 'ctrl b':
        return 'page up'
    return key

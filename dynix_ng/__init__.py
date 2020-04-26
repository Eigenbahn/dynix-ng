#!/usr/bin/env python3

import os
import sys
from pprint import pprint
import locale

import datetime

import curses
from curses import wrapper

main_path = os.path.dirname(os.path.realpath(__file__))
module_path = os.path.abspath(main_path + '/..')
if module_path not in sys.path:
    sys.path.append(module_path)

from dynix_ng.utils.curses.textpad import CustomTextbox
from dynix_ng.utils.curses.print import addstr_x_centered

from dynix_ng.library.backend.calibre import CalibreDb



# ENCODING

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()



# CONF

HALF_DELAY = 5
# How many tenths of a second are waited, from 1 to 255

SCREENS = {
    'welcome': '',
    'title_list': 'TITLE Keywords',
    'title_search_exact': 'Exact TITLE',
    'author_list': 'AUTHOR Browse',
    'subject_list': 'SUBJECT Keywords',
    'series_list': 'SERIES',
    'super_search': 'SUPER Search',

    'newspaper_search': 'Newspaper Keyword Search',
    'newspaper_subject_search': 'Newspaper Subject Search',

    'best_books_list': 'Best Sellers and Award Books',

    'additional_searches': 'Additional Searches',
    'patron_record': 'Review Patron Record',

    'quit': 'Logoff',
}

WELCOME_MESSAGE = ["Welcome to the Online Public Access Catalog!",
                   "Please select one of the options below."]



# HELPERS: TIME

def now_as_str():
    now = datetime.datetime.now()
    now_str = now.strftime("%I:%M:%S%p").lower()
    return now_str



# SCREEN FNS

def draw_modem_header(win):
    # NB: this might correcpond to the modem
    # FDX probably means full duplex
    header_txt = " " * 8 + "FDX" + " " * 4 + "10:32p  22- 48"
    # NB: this -1 should not be needed but doesn't work on a vterm if not set
    # header_txt += " " * (curses.COLS - len(header_txt))
    header_txt += " " * (curses.COLS - len(header_txt) - 1)

    win.addstr(0, 0, header_txt, curses.A_UNDERLINE)


def draw_header(win):
    now = datetime.datetime.now()
    today_str = now.strftime("%d %b %Y").upper()
    now_str = now.strftime("%I:%M:%S%p").lower()
    now_str_modem = now_str[:-1]

    # library_name = 'GOSHEN PUBLIC LIBRARY'
    library_name = 'EIGENBAHN PRIVATE LIBRARY'

    win.addstr(0, 1, " " * (curses.COLS - 2), curses.A_REVERSE)
    win.addstr(0, 2, today_str, curses.A_REVERSE)
    addstr_x_centered(win, 1, library_name, curses.A_REVERSE)

    # addstr_x_centered(stdscr, 1, " Dial Pac ", curses.A_REVERSE)

# TODO: class to split draw / input logic into 2 methods
def draw_screen_welcome(win, inputwin):
    (lines, cols) = win.getmaxyx()

    y = 2

    # welcome banner
    for message in WELCOME_MESSAGE:
        addstr_x_centered(win, y, message)
        y += 1

    y += 1

    # menu
    i = 1
    for screen_menu_desc in list(SCREENS.values())[1:]:
        num_sep = "  "
        if i >= 10:
            num_sep = " "
        menu_entry = 25 * " " + str(i) + "." + num_sep + screen_menu_desc
        win.addstr(y, 0, menu_entry)
        i += 1
        y += 1

    y += 4

    # input
    prompt_text = " Enter your selection(s) and press <Enter> : "
    win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)

    # shortcuts
    win.addstr(lines - 1, 0, "S=Shortcut on, BB=Bulleton Board, ?=Help")

    box = CustomTextbox(inputwin)
    user_input = box.edit() # NB: breaks after `HALF_DELAY`

    if user_input != curses.ERR:
        return list(SCREENS.keys())[int(user_input)]
    return curses.ERR



# HELPERS: FORMAT TIME

def now_as_str():
    now = datetime.datetime.now()
    now_str = now.strftime("%I:%M:%S%p").lower()
    return now_str


# GLOBAL VARS

user_input = ""

# display_modem_header = True
display_modem_header = False



# DEBUG

# db = CalibreDb()
# pprint(db.book_list(fetch_mode='all'))
# exit()


# SCRIPT

def main(stdscr):
    global user_input

    db = CalibreDb()

    win_list = []

    curses.halfdelay(HALF_DELAY)
    curses.noecho() # no input repeat

    y = 0

    if display_modem_header:
        modem_header_win = curses.newwin(1, curses.COLS, y, 0)
        win_list.append(modem_header_win)
        y += 1

    header_win = curses.newwin(2, curses.COLS, y, 0)
    win_list.append(header_win)
    y += 2

    screen_win = curses.newwin(curses.LINES - y, curses.COLS, y, 0)
    win_list.append(screen_win)

    prompt_text = " Enter your selection(s) and press <Enter> : "
    input_len = 2
    input_win = curses.newwin(1, input_len + 1, curses.LINES - 2, len(prompt_text) + 1)
    win_list.append(input_win)

    while True:

        stdscr.clear()

        if display_modem_header:
            draw_modem_header(modem_header_win)
        draw_header(header_win)

        # NB: breaks after `HALF_DELAY`
        user_input = draw_screen_welcome(screen_win, input_win)

        # refresh screen
        # header_win.addstr(0, 0, now_as_str())

        for w in win_list:
            w.refresh()

        if user_input != curses.ERR:
            # actual input (not halfdelay)
            break


if __name__ == "__main__":
    wrapper(main)
    print('got: ' + user_input)

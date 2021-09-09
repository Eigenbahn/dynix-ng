#!/usr/bin/env python3

import os
import sys
from pprint import pprint
import locale

import time
import datetime

import curses
from curses import wrapper

main_path = os.path.dirname(os.path.realpath(__file__))
module_path = os.path.abspath(main_path + '/..')
if module_path not in sys.path:
    sys.path.append(module_path)

from dynix_ng.ui.session import DynixSession, DynixSearch
from dynix_ng.ui.screen import WelcomeScreen, SearchScreen, CounterScreen, SummaryScreen, ItemScreen
from dynix_ng.ui.header import draw_modem_header, draw_dynix_header

from dynix_ng.utils.curses.textpad import CustomTextbox
from dynix_ng.utils.curses.print import addstr_x_centered

from dynix_ng.library.backend.calibre import CalibreDb
from dynix_ng.library.backend.archive import ArchiveOrgApi

import dynix_ng.utils.query.recall as recall

import dynix_ng.state.memory as global_state



# CONF: ENCODING

# locale.setlocale(locale.LC_ALL, '')
# code = locale.getpreferredencoding()



# CONF: CURSES

HALF_DELAY = 5
# How many tenths of a second are waited, from 1 to 255



# CONF

DISPLAY_SECONDS = True

LIBRARY_NAME = 'EIGENBAHN PRIVATE LIBRARY'
# LIBRARY_NAME = 'GOSHEN PUBLIC LIBRARY'


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

SCREENS = {
    'welcome': '',
    'author_search_alpha': 'AUTHOR Alphabetical Search',
    'title_search_alpha': 'Alphabetical TITLE Search',
    'title_search_keyword': 'TITLE Keyword Search',
    'word_search_general': 'GENERAL Word Search',
    'subject_search': 'SUBJECT INDEX FILE Search',
    '653_search_authority': '653 SUBJECT Authority Search',
    '653_search_keyword': '653 SUBJECT Keyword Search',
    'series_search_keyword': 'SERIES Keyword Search',
    'series_search_authority': 'SERIES Authority Search',

    'dewey_search': 'DEWEY Decimal Class No. Search',
    'universal_id_search': 'ISBN/ISSN/OCLC No. Search',
    'barcode_search': 'Item BARCODE Search',
    'bib_search': 'Dynix BIB No. Search',
    'class_search_authority': 'CLASS Authority Search',
    'pub_search_alpha': 'PUBLISHER Alphabetical Search',
    # 'polytek_db': 'Polytechnic Resources Database',
    'title_search_archive.org': 'TITLE Archive.Org search',

    'quit': 'Quit searching',
}

SEARCH_SCREENS = [
    # Calibre
    'author_search_alpha',
    'pub_search_alpha',
    'title_search_alpha', 'title_search_keyword',
    'subject_search',
    'word_search_general',
    'series_search_keyword', 'series_search_authority'
    'universal_id_search',
    'bib_search',

    # Archive.Org
    'title_search_archive.org',
]


WELCOME_MESSAGE = ["Welcome to the Online Public Access Catalog!",
                   "Please select one of the options below."]


SCREEN_PROMPT_WELCOME = "Enter your selection(s) and press <Enter> :"
# menu_desc_list = list(SCREENS.values())[1:]
# SCREEN_PROMPT_WELCOME = "Enter your selection (1-" + str(len(menu_desc_list)) + ") and press <Return> :"

SCREEN_PROMPT_SEARCH_TITLE = "Enter TITLE keywords :"

SCREEN_PROMPT_COUNTER = "Type additional word(s) :"

SCREEN_PROMPT_ITEM = "Press <Return> to see next screen :"

SCREEN_PROMPTS = {
    'welcome': SCREEN_PROMPT_WELCOME,
    'title_search_alpha': SCREEN_PROMPT_SEARCH_TITLE,
    'title_search_keyword': SCREEN_PROMPT_SEARCH_TITLE,
    'title_search_archive.org': SCREEN_PROMPT_SEARCH_TITLE,
    'search_counter': SCREEN_PROMPT_COUNTER,
    'summary': SCREEN_PROMPT_COUNTER,
    'item_view': SCREEN_PROMPT_ITEM,
}

def get_input_length(screen_id):
    if screen_id == 'welcome':
        return 2
    elif screen_id in SEARCH_SCREENS:
        return 20
    elif global_state.session.screen_id == 'search_counter':
        return 15
    elif global_state.session.screen_id == 'summary':
        return 2
    elif global_state.session.screen_id == 'item_view':
        return 2
    return 0

# DISPLAY_MODEM_HEADER = True
DISPLAY_MODEM_HEADER = False



# GLOBAL VARS

static_screens = {}

recall_query = []

results = None

# backends
calibreBackend = CalibreDb()
archiveOrgBackend = ArchiveOrgApi()



# DEBUG

# db = CalibreDb()
# recall_query = recall.user_query_to_recall("stat?")
# where = recall.recall_to_sql(['title'], recall_query, 'sqlite3')
# res = db.item_list(fetch_mode='all', fetch_format='k_v', where=where, detailed=True)
# pprint(res)
# exit()


## TRANSITION

def screen_change(new_screen_id):
    global static_screens
    global SCREENS
    global SEARCH_SCREENS
    global SCREEN_PROMPT_WELCOME, SCREEN_PROMPT_SEARCH_TITLE, SCREEN_PROMPT_COUNTER, SCREEN_PROMPT_ITEM

    session = global_state.session

    global_state.screen_win.clear()

    if not global_state.session.screen_id in static_screens.keys():
        del global_state.session.screen # free memory

    session.screen_id = new_screen_id
    input_prompt = global_state.screen_prompt_list[session.screen_id]
    input_y = len(input_prompt) + 2 + 1
    input_len = get_input_length(new_screen_id)
    global_state.inputwin = curses.newwin(1, input_len + 1, curses.LINES - 2, input_y)

    if global_state.session.screen_id in static_screens.keys():
        global_state.session.screen = static_screens[global_state.session.screen_id]
    # elif session.screen_id == 'title_search_keyword':
    elif session.screen_id == 'welcome':
        session.screen = WelcomeScreen()
    elif session.screen_id in SEARCH_SCREENS:
        session.screen = SearchScreen()
    elif session.screen_id == 'search_counter':
        session.screen = CounterScreen()
    elif session.screen_id == 'summary':
        session.screen = SummaryScreen()
    elif session.screen_id == 'item_view':
        session.screen = ItemScreen()
    else:
        # TODO: throw exception
        pass


def search_screen_to_search_type (screen_id):
    if screen_id == 'author_search_alpha':
        return 'author'
    elif screen_id == 'pub_search_alpha':
        return 'publisher'
    elif screen_id in ['title_search_alpha', 'title_search_keyword',
                       'title_search_archive.org']:
        return 'title'
    elif screen_id == 'subject_search':
        return 'subject'
    elif screen_id == 'word_search_general':
        return 'word'
    elif screen_id in ['series_search_keyword', 'series_search_authority']:
        return 'series'
    elif screen_id == 'universal_id_search':
        return 'universal_id'
    elif screen_id == 'bib_search':
        return 'bib'

def search_screen_to_backend (screen_id):
    global calibreBackend
    if screen_id == 'author_search_alpha':
        return calibreBackend
    elif screen_id == 'pub_search_alpha':
        return calibreBackend
    elif screen_id in ['title_search_alpha', 'title_search_keyword']:
        return calibreBackend
    elif screen_id == 'subject_search':
        return calibreBackend
    elif screen_id == 'word_search_general':
        return calibreBackend
    elif screen_id in ['series_search_keyword', 'series_search_authority']:
        return calibreBackend
    elif screen_id == 'universal_id_search':
        return calibreBackend
    elif screen_id == 'bib_search':
        return calibreBackend
    elif screen_id == 'title_search_archive.org':
        return archiveOrgBackend


## NB: deprecated
def search_screen_to_backend_fields (backend, screen_id):
    if screen_id == 'author_search_alpha':
        return ['author']
    elif screen_id == 'pub_search_alpha':
        return ['publisher']
    elif screen_id in ['title_search_alpha', 'title_search_keyword',
                       'title_search_archive.org']:
        return ['title']
    elif screen_id == 'subject_search':
        return ['tag']
    elif screen_id == 'word_search_general':
        return ['author', 'publisher', 'title', 'subject', 'series']
    elif screen_id in ['series_search_keyword', 'series_search_authority']:
        return ['series']
    elif screen_id == 'universal_id_search':
        return ['ISBN', 'LCCN']
    elif screen_id == 'bib_search':
        return ['item_id']


def handle_user_input():
    session = global_state.session

    if session.screen_id == 'welcome':
        if session.user_input in list(SCREENS.keys()):
            screen_change(session.user_input)
    elif session.screen_id == 'search_counter':
        if session.user_input.upper() == 'D': # Show all results
            screen_change('summary')
            # elif session.screen_id == 'title_search_keyword':
    elif session.screen_id in SEARCH_SCREENS:
        if session.user_input.upper() in ['SO', 'Q']: # Start Over / Quit current search
            screen_change('welcome')
        elif session.user_input.upper() in ['P', 'B']: # Previous page / Back to previous search level
            screen_change('welcome')
        else:
            user_query = session.user_input
            search_type = search_screen_to_search_type(session.screen_id)
            backend = search_screen_to_backend(session.screen_id)
            session.search = DynixSearch(user_query, backend, search_type)
            # NB: systematic transition to search counter screen before search summary to mimick original behaviour
            screen_change('search_counter')
            if session.search.results_total_count <= 30:
                time.sleep(0.1)
                screen_change('summary')
    elif session.screen_id == 'summary':
        if session.user_input.upper() in ['SO', 'Q']: # Start Over / Quit current search
            screen_change('welcome')
        elif session.user_input.upper() in ['P', 'B']: # Previous page / Back to previous search level
            if session.search.results_total_count > 30:
                screen_change('search_counter')
            else:
                screen_change('title_search_keyword')
        elif session.user_input.isdigit():
            session.item_id = int(session.user_input)
            session.item = list(session.search.results.values())[session.item_id - 1]
            screen_change('item_view')
    elif session.screen_id == 'item_view':
        if session.user_input.upper() in ['SO', 'Q']: # Start Over / Quit current search
            screen_change('welcome')
        if session.user_input.upper() in ['P', 'B']: # Previous page / Back to previous search level
            screen_change('summary')
        elif session.user_input.upper() == 'PT': # Previous Title
            if session.item_id > 1:
                session.item_id -= 1
                session.item = list(session.search.results.values())[session.item_id - 1]
                screen_change('item_view')
        elif session.user_input.upper() == 'NT': # Next Title
            if session.item_id < session.search.results_total_count:
                session.item_id += 1
                session.item = list(session.search.results.values())[session.item_id - 1]
                screen_change('item_view')
    else:
        return "exit"




## SCRIPT

def main(stdscr):
    # headers
    global DISPLAY_MODEM_HEADER
    global LIBRARY_NAME, DISPLAY_SECONDS

    global SCREENS
    global SEARCH_SCREENS

    win_list = []

    curses.halfdelay(HALF_DELAY)
    curses.noecho() # no input repeat

    y = 0

    if DISPLAY_MODEM_HEADER:
        modem_header_win = curses.newwin(1, curses.COLS, y, 0)
        win_list.append(modem_header_win)
        y += 1

    header_win = curses.newwin(2, curses.COLS, y, 0)
    win_list.append(header_win)
    y += 2

    global_state.screen_win = curses.newwin(curses.LINES - y, curses.COLS, y, 0)

    global_state.session = DynixSession()
    global_state.screen_list = SCREENS
    global_state.welcome_message = WELCOME_MESSAGE
    global_state.screen_prompt_list = SCREEN_PROMPTS

    screen_change('welcome')
    # screen_welcome = WelcomeScreen(global_state.session.screen_id)
    # static_screens[global_state.session.screen_id] = screen_welcome
    # global_state.session.screen = screen_welcome


    running = True
    while running:

        stdscr.clear()

        if DISPLAY_MODEM_HEADER:
            draw_modem_header(modem_header_win)
        draw_dynix_header(header_win, LIBRARY_NAME, DISPLAY_SECONDS)

        global_state.session.screen.draw()

        # NB: breaks after `HALF_DELAY`
        user_input = global_state.session.screen.get_input()

        for w in win_list:
            w.refresh()
        global_state.session.screen.refresh()

        if user_input == curses.ERR: # halfdelay
            continue

        # NB: curses box has a tendency to add a trailing space when pressing <Return>
        global_state.session.user_input = user_input.strip()

        next_action = handle_user_input()
        if next_action == "exit":
            running = False


## START

if __name__ == "__main__":
    try:
        wrapper(main)
        print('got: "' + global_state.session.user_input +'"')
    except KeyboardInterrupt:
        print('bye!')

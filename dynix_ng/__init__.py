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

from dynix_ng.ui.screen import WelcomeScreen, SearchScreen, CounterScreen, SummaryScreen, ItemScreen
from dynix_ng.ui.header import draw_modem_header, draw_dynix_header

from dynix_ng.utils.curses.textpad import CustomTextbox
from dynix_ng.utils.curses.print import addstr_x_centered

from dynix_ng.library.backend.calibre import CalibreDb

import dynix_ng.utils.query.recall as recall


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
    'polytek_db': 'Polytechnic Resources Database',

    'quit': 'Quit searching',
}


WELCOME_MESSAGE = ["Welcome to the Online Public Access Catalog!",
                   "Please select one of the options below."]


SCREEN_PROMPT_WELCOME = "Enter your selection(s) and press <Enter> :"
# menu_desc_list = list(SCREENS.values())[1:]
# SCREEN_PROMPT_WELCOME = "Enter your selection (1-" + str(len(menu_desc_list)) + ") and press <Return> :"

SCREEN_PROMPT_SEARCH_TITLE = "Enter TITLE keywords :"

SCREEN_PROMPT_COUNTER = "Type additional word(s) :"

SCREEN_PROMPT_ITEM = "Press <Return> to see next screen :"


# DISPLAY_MODEM_HEADER = True
DISPLAY_MODEM_HEADER = False



# GLOBAL VARS

current_screen_id = 'welcome'
current_screen = None

user_input = ""

user_query = ""
recall_query = []

results = None



# DEBUG

# db = CalibreDb()
# recall_query = recall.user_query_to_recall("stat?")
# where = recall.recall_to_sql('title', recall_query, 'sqlite3')
# res = db.book_list(fetch_mode='all', fetch_format='k_v', where=where, detailed=True)
# pprint(res)
# exit()


# SCRIPT


def main(stdscr):
    global user_input
    global results
    global current_screen_id
    global current_screen

    # current search
    global user_query, recall_query

    # headers
    global DISPLAY_MODEM_HEADER
    global LIBRARY_NAME, DISPLAY_SECONDS

    global SCREENS

    # PROMPTS
    global SCREEN_PROMPT_WELCOME, SCREEN_PROMPT_SEARCH_TITLE, SCREEN_PROMPT_COUNTER, SCREEN_PROMPT_ITEM


    db = CalibreDb()

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

    screen_win = curses.newwin(curses.LINES - y, curses.COLS, y, 0)

    screen_welcome = WelcomeScreen(current_screen_id, SCREENS[current_screen_id], screen_win, SCREEN_PROMPT_WELCOME, 2, WELCOME_MESSAGE, SCREENS)
    current_screen = screen_welcome


    while True:

        stdscr.clear()

        if DISPLAY_MODEM_HEADER:
            draw_modem_header(modem_header_win)
        draw_dynix_header(header_win, LIBRARY_NAME, DISPLAY_SECONDS)

        current_screen.draw()

        # NB: breaks after `HALF_DELAY`
        user_input = current_screen.get_input()

        for w in win_list:
            w.refresh()
        current_screen.refresh()



        if user_input != curses.ERR: # actual input (not halfdelay)

            # NB: curses box has a tendency to add a trailing space when pressing <Return>
            user_input = user_input.strip()

            if current_screen_id == 'welcome':
                if user_input in list(SCREENS.keys()):
                    current_screen_id = user_input
                    screen_win.clear()
                    if current_screen_id == 'title_search_keyword':
                        current_screen = SearchScreen(current_screen_id, SCREENS[current_screen_id], screen_win, SCREEN_PROMPT_SEARCH_TITLE, 20)
                else:
                    # TODO: throw exception
                    break
            elif current_screen_id == 'search_counter':
                if user_input.upper() == 'D': # Show all results
                    screen_win.clear()

                    nb_items = current_screen.count_total
                    current_screen_id = 'summary'
                    current_screen = SummaryScreen(current_screen_id, "", screen_win, SCREEN_PROMPT_COUNTER, 2,
                                                   db, recall_query, 'title', nb_items)

            elif current_screen_id == 'title_search_keyword':
                if user_input.upper() == 'SO': # Start Over
                    screen_win.clear()
                    current_screen_id = 'welcome'
                    current_screen = screen_welcome
                else:
                    user_query = user_input
                    recall_query = recall.user_query_to_recall(user_input)
                    # where = recall.recall_to_sql('title', recall_query, 'sqlite3')
                    # results = db.book_list(fetch_mode='all', where=where)

                    screen_win.clear()
                    current_screen_id = 'search_counter'
                    current_screen = CounterScreen(current_screen_id, "", screen_win, SCREEN_PROMPT_COUNTER, 15,
                                                   db, recall_query, 'title')

                    if current_screen.count_total <= 30:
                        nb_items = current_screen.count_total
                        current_screen_id = 'summary'
                        current_screen = SummaryScreen(current_screen_id, "", screen_win, SCREEN_PROMPT_COUNTER, 2,
                                                       db, recall_query, 'title', nb_items)


                        # results = current_screen.recall_query_results
                        # break


            elif current_screen_id == 'summary':
                if user_input.upper() == 'SO': # Start Over
                    screen_win.clear()
                    current_screen_id = 'welcome'
                    current_screen = screen_welcome
                elif user_input.isdigit():
                    item_id = int(user_input)
                    recall_query = current_screen.recall_query
                    recall_query_results = current_screen.recall_query_results
                    item = list(recall_query_results.values())[item_id]

                    # results = item
                    # break

                    del current_screen # free memory

                    screen_win.clear()
                    current_screen_id = 'item_view'
                    current_screen = ItemScreen(current_screen_id, "", screen_win, SCREEN_PROMPT_ITEM, 2, recall_query, recall_query_results, item)

            else:
                break

if __name__ == "__main__":
    try:
        wrapper(main)
        print('got: "' + user_input +'"')
        if results:
            pprint(results)
    except KeyboardInterrupt:
        print('bye!')

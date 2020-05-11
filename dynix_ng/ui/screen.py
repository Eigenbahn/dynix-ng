#!/usr/bin/env python3

from abc import ABC, abstractmethod

import curses

from dynix_ng.utils.curses.textpad import CustomTextbox
from dynix_ng.utils.curses.print import addstr_x_centered, addstr_rigth_x

import dynix_ng.utils.query.recall as recall



# ABSTRACT CLASS

class DynixScreen(ABC):

    def __init__(self, screen_id, desc, win, input_prompt, input_len):
        self.screen_id = screen_id
        self.desc = desc

        self.win = win
        (self.lines, self.cols) = self.win.getmaxyx()

        self.input_prompt = input_prompt
        input_y = len(self.input_prompt) + 2 + 1
        self.inputwin = curses.newwin(1, input_len + 1, curses.LINES - 2, input_y)

    def draw(self):
        pass

    def get_input(self):
        pass

    def refresh(self):
        self.win.refresh()
        self.inputwin.refresh()



# MAIN MENU SCREEN

class WelcomeScreen(DynixScreen):

    def __init__(self, screen_id, desc, win, input_prompt, input_len,
                 welcome_message, screens):
        self.screens = screens
        self.welcome_message = welcome_message
        super().__init__(screen_id, desc, win, input_prompt, input_len)


    def draw(self):
        (lines, cols) = self.win.getmaxyx()

        y = 2

        # welcome banner
        for message in self.welcome_message:
            addstr_x_centered(self.win, y, message)
        y += 1

        # menu
        i = 1
        menu_start_y = y
        menu_desc_list = list(self.screens.values())[1:]
        is_dual_pane = len(menu_desc_list) > lines - menu_start_y - 3
        # is_dual_pane = True
        dual_pane_nb_elems = 9

        for screen_menu_desc in menu_desc_list:
            num_sep = "  "
            if is_dual_pane or i >= 10:
                num_sep = " "

            x = 25
            if is_dual_pane:
                x = 4
                if i > dual_pane_nb_elems:
                    x = cols - 33 - 4

            menu_entry = str(i) + "." + num_sep + screen_menu_desc
            self.win.addstr(y, x, menu_entry)
            i += 1
            y += 1
            if is_dual_pane and i == dual_pane_nb_elems + 1:
                y = menu_start_y

        # input
        prompt_text = " " + self.input_prompt +  " "
        # prompt_text = " Enter your selection (1-" + str(len(menu_desc_list)) + ") and press <Return> : "
        self.win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)

        # shortcuts
        self.win.addstr(lines - 1, 0, "S=Shortcut on, BB=Bulleton Board, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`
        if user_input != curses.ERR:
            try:
                    return list(self.screens.keys())[int(user_input)]
            except:
                return user_input
        return curses.ERR



# SEARCH SCREEN

class SearchScreen(DynixScreen):

    def draw(self):
        (lines, cols) = self.win.getmaxyx()

        y = 1

        addstr_x_centered(self.win, y, self.desc)
        y += 1

        y += 4

        self.win.addstr(y, 4, "Examples:")
        y += 1
        for example in ('HUCKLEBERRY (Single word search)',
                        'GONE WIND (Multiple word search)',
                        'COMPUT? (For words starting with COMPUT...)'):
            self.win.addstr(y, 15, example)
            y += 2
        # input
        prompt_text = " " + self.input_prompt +  " "
        self.win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)
        # shortcuts
        self.win.addstr(lines - 1, 0, "Commands: SO=Start Over, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR



# SEARCH RESULT COUNTER SCREEN

class CounterScreen(DynixScreen):
    def __init__(self, screen_id, desc, win, input_prompt, input_len,
                 db, recall_query,
                 db_field):
        self.db = db
        self.db_field = db_field
        self.recall_query = recall_query

        self.recall_query_results = {}
        incremental_terms = []
        for term in self.recall_query:
            incremental_terms.append(term)
            where = recall.recall_to_sql(db_field, incremental_terms, 'sqlite3')
            count = db.book_list(fetch_mode='first', fetch_format='count', where=where)
            self.recall_query_results[term] = count

        self.count_total = list(self.recall_query_results.values())[-1]

        super().__init__(screen_id, desc, win, input_prompt, input_len)


    def draw(self):
        (lines, cols) = self.win.getmaxyx()

        y = 1

        self.win.addstr(y, 5, " ".join(self.recall_query))
        self.win.addstr(y, 5 + 20 + 2, "Total=" + str(self.count_total))
        y += 1

        self.win.addstr(y, 4, "Searching...                Running Total")
        y += 2

        for term, count in self.recall_query_results.items():
            self.win.addstr(y, 4, term)
            self.win.addstr(y, 25, str(count))
            y += 1

        self.win.addstr(lines - 7, 4, "titles matched     " + str(self.count_total))

        self.win.addstr(lines - 5, 4, "To narrow the search, enter more words.")
        self.win.addstr(lines - 4, 4, "Or, press 'D' and <Return> to see all " + str(self.count_total) + " titles.")

        # input
        prompt_text = " " + self.input_prompt +  " "
        self.win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)
        # shortcuts
        self.win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, D=Display, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR



# SEARCH SUMMARY SCREEN

class SummaryScreen(DynixScreen):

    def __init__(self, screen_id, desc, win, input_prompt, input_len,
                 db, recall_query,
                 db_field,
                 nb_items):
        self.db = db
        self.db_field = db_field
        self.recall_query = recall_query

        self.count_total = nb_items

        where = recall.recall_to_sql(db_field, recall_query, 'sqlite3')
        self.recall_query_results = db.book_list(fetch_mode='all', fetch_format='k_v', where=where, detailed=True)

        super().__init__(screen_id, desc, win, input_prompt, input_len)

    def draw(self):
        (lines, cols) = self.win.getmaxyx()

        y = 1

        # query
        self.win.addstr(y, 4, "Your search:  " + ' '.join(self.recall_query))
        y += 1

        # table header
        self.win.addstr(y, 6, "AUTHOR")
        addstr_x_centered(self.win, y, "TITLE")
        self.win.addstr(y, cols - 15, "DATE")
        y += 1

        # results table
        i = 1
        for item_id, item in self.recall_query_results.items():
            author_summary = ' - '.join(item['authors_sorted'])
            pub_date = item['pub_date'][:10]
            if pub_date == '0101-01-01':
                pub_date = '????'
            # TODO: word wrap
            # title_n_ndate = item['sorted_name'] + ' ' + pub_date
            self.win.addstr(y, 2, str(i) + ". " + author_summary)
            y += 1
            # self.win.addstr(y, 6, title_n_ndate)
            self.win.addstr(y, 6, item['sorted_name'])
            self.win.addstr(y, cols - 15, pub_date)
            i += 1
            y += 1

        # paging
        # TODO: right-align
        self.win.addstr(lines - 3, 0, "---" + str(self.count_total) + " titles, End of List" + "---")

        # shortcuts
        self.win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, D=Display, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR



# ITEM SCREEN

class ItemScreen(DynixScreen):

    def __init__(self, screen_id, desc, win, input_prompt, input_len,
                 recall_query, recall_query_results, item):
        self.recall_query = recall_query
        self.recall_query_results = recall_query_results
        self.item = item

        super().__init__(screen_id, desc, win, input_prompt, input_len)

    def draw(self):
        (lines, cols) = self.win.getmaxyx()

        y = 1

        props_x = 9 + 7 + 2

        # query
        addstr_rigth_x(self.win, y, 16, "Call Number:  ")
        self.win.addstr(y, props_x, str(self.item['book_id']))
        y += 2

        addstr_rigth_x(self.win, y, 16, "AUTHOR:")

        for i, a in enumerate(self.item['authors_sorted'], start=1):
            self.win.addstr(y, props_x, str(i) + ") " + a)
            y += 1
        y += 1

        addstr_rigth_x(self.win, y, 16, "TITLE:")
        # TODO: word wrap
        self.win.addstr(y, props_x, self.item['sorted_name'])
        y += 2

        # addstr_rigth_x(self.win, y, 16, "PUBLISHER:")
        addstr_rigth_x(self.win, y, 16, "IMPRINT:")
        self.win.addstr(y, props_x, ' - '.join(self.item['publishers']))
        y += 2

        # addstr_rigth_x(self.win, y, 16, "TAGS:")
        addstr_rigth_x(self.win, y, 16, "SUBJECTS:")
        for i, t in enumerate(self.item['tags'], start=1):
            self.win.addstr(y, props_x, str(i) + ") " + t)
            y += 1
        y += 1


        # TODO: word wrap
        # self.win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, RW=Related Works, S=Select, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR

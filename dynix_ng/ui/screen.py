#!/usr/bin/env python3

from abc import ABC, abstractmethod

import curses

from dynix_ng.utils.curses.textpad import CustomTextbox
from dynix_ng.utils.curses.print import addstr_x_centered, addstr_rigth_x

import dynix_ng.utils.query.recall as recall

import dynix_ng.state.memory as global_state



# ABSTRACT CLASS

class DynixScreen(ABC):

    def __init__(self, screen_id, desc, input_prompt, input_len):
        self.screen_id = screen_id
        self.desc = desc

        self.input_prompt = input_prompt
        input_y = len(self.input_prompt) + 2 + 1
        self.inputwin = curses.newwin(1, input_len + 1, curses.LINES - 2, input_y)

    def draw(self):
        pass

    def get_input(self):
        pass

    def refresh(self):
        global_state.screen_win.refresh()
        self.inputwin.refresh()

    def handle_user_input(self, user_input, SCREENS):
        pass



# MAIN MENU SCREEN

class WelcomeScreen(DynixScreen):

    def __init__(self, screen_id, desc, input_prompt, input_len,
                 welcome_message, screens):
        self.screens = screens
        self.welcome_message = welcome_message
        super().__init__(screen_id, desc, input_prompt, input_len)

    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()

        y = 2

        # welcome banner
        for message in self.welcome_message:
            addstr_x_centered(global_state.screen_win, y, message)
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
            global_state.screen_win.addstr(y, x, menu_entry)
            i += 1
            y += 1
            if is_dual_pane and i == dual_pane_nb_elems + 1:
                y = menu_start_y

        # input
        prompt_text = " " + self.input_prompt +  " "
        # prompt_text = " Enter your selection (1-" + str(len(menu_desc_list)) + ") and press <Return> : "
        global_state.screen_win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)

        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "S=Shortcut on, BB=Bulleton Board, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`
        if user_input != curses.ERR:
            try:
                    return list(self.screens.keys())[int(user_input)]
            except:
                return user_input
        return curses.ERR

    def handle_user_input(self, user_input, SCREENS):
        if user_input in list(SCREENS.keys()):
            return {'action': 'change_screen',
                    'screen_id': user_input}



# SEARCH SCREEN

class SearchScreen(DynixScreen):

    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()

        y = 1

        addstr_x_centered(global_state.screen_win, y, self.desc)
        y += 1

        y += 4

        global_state.screen_win.addstr(y, 4, "Examples:")
        y += 1
        for example in ('HUCKLEBERRY (Single word search)',
                        'GONE WIND (Multiple word search)',
                        'COMPUT? (For words starting with COMPUT...)'):
            global_state.screen_win.addstr(y, 15, example)
            y += 2
        # input
        prompt_text = " " + self.input_prompt +  " "
        global_state.screen_win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)
        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR

    def handle_user_input(self, user_input, SCREENS):
        if user_input.upper() == 'SO': # Start Over
            return {'action': 'change_screen',
                    'screen_id': 'welcome'}
        else:
            return {'action': 'search',
                    'query': user_input}



# SEARCH RESULT COUNTER SCREEN

class CounterScreen(DynixScreen):
    def __init__(self, screen_id, desc, input_prompt, input_len):

        global_state.session.search_stage = 'count'
        global_state.session.search.query_count_incremental()

        super().__init__(screen_id, desc, input_prompt, input_len)


    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()

        nb_total = str(global_state.session.search.results_total_count)

        y = 1

        global_state.screen_win.addstr(y, 5, " ".join(global_state.session.search.recall_query))
        global_state.screen_win.addstr(y, 5 + 20 + 2, "Total=" + nb_total)
        y += 1

        global_state.screen_win.addstr(y, 4, "Searching...                Running Total")
        y += 2

        for term, count in global_state.session.search.results_incremental_counts.items():
            global_state.screen_win.addstr(y, 4, term)
            global_state.screen_win.addstr(y, 25, str(count))
            y += 1

        global_state.screen_win.addstr(lines - 7, 4, "titles matched     " + nb_total)

        global_state.screen_win.addstr(lines - 5, 4, "To narrow the search, enter more words.")
        global_state.screen_win.addstr(lines - 4, 4, "Or, press 'D' and <Return> to see all " + nb_total + " titles.")

        # input
        prompt_text = " " + self.input_prompt +  " "
        global_state.screen_win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)
        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, D=Display, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR

    def handle_user_input(self, user_input, SCREENS):
        if user_input.upper() == 'D': # Show all results
            return {'action': 'change_screen',
                    'screen_id': 'welcome'}
        else:
            return {'action': 'search',
                    'query': user_input}



# SEARCH SUMMARY SCREEN (LIST OF RESULTS)

class SummaryScreen(DynixScreen):

    def __init__(self, screen_id, desc, input_prompt, input_len):

        global_state.session.search_stage = 'summary'
        global_state.session.search.query()

        super().__init__(screen_id, desc, input_prompt, input_len)

    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()

        y = 1

        # query
        global_state.screen_win.addstr(y, 4, "Your search:  " + ' '.join(global_state.session.search.recall_query))
        y += 1

        # table header
        global_state.screen_win.addstr(y, 6, "AUTHOR")
        addstr_x_centered(global_state.screen_win, y, "TITLE")
        global_state.screen_win.addstr(y, cols - 15, "DATE")
        y += 1

        # results table
        i = 1
        for item_id, item in global_state.session.search.results.items():
            author_summary = ' - '.join(item['authors_sorted'])
            pub_date = item['pub_date'][:10]
            if pub_date == '0101-01-01':
                pub_date = '????'
            # TODO: word wrap
            # title_n_ndate = item['sorted_name'] + ' ' + pub_date
            global_state.screen_win.addstr(y, 2, str(i) + ". " + author_summary)
            y += 1
            # global_state.screen_win.addstr(y, 6, title_n_ndate)
            global_state.screen_win.addstr(y, 6, item['sorted_name'])
            global_state.screen_win.addstr(y, cols - 15, pub_date)
            i += 1
            y += 1

        # paging
        # TODO: right-align
        global_state.screen_win.addstr(lines - 3, 0, "---" + str(global_state.session.search.results_total_count) + " titles, End of List" + "---")

        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, D=Display, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR



# ITEM SCREEN

class ItemScreen(DynixScreen):

    def __init__(self, screen_id, desc, input_prompt, input_len):
        global_state.session.search_stage = 'item'
        super().__init__(screen_id, desc, input_prompt, input_len)

    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()

        y = 1

        props_x = 9 + 7 + 2

        # query
        addstr_rigth_x(global_state.screen_win, y, 16, "Call Number:  ")
        global_state.screen_win.addstr(y, props_x, str(global_state.session.item['book_id']))
        y += 2

        addstr_rigth_x(global_state.screen_win, y, 16, "AUTHOR:")

        for i, a in enumerate(global_state.session.item['authors_sorted'], start=1):
            global_state.screen_win.addstr(y, props_x, str(i) + ") " + a)
            y += 1
        y += 1

        addstr_rigth_x(global_state.screen_win, y, 16, "TITLE:")
        # TODO: word wrap
        global_state.screen_win.addstr(y, props_x, global_state.session.item['sorted_name'])
        y += 2

        # addstr_rigth_x(global_state.screen_win, y, 16, "PUBLISHER:")
        addstr_rigth_x(global_state.screen_win, y, 16, "IMPRINT:")
        global_state.screen_win.addstr(y, props_x, ' - '.join(global_state.session.item['publishers']))
        y += 2

        # addstr_rigth_x(global_state.screen_win, y, 16, "TAGS:")
        addstr_rigth_x(global_state.screen_win, y, 16, "SUBJECTS:")
        for i, t in enumerate(global_state.session.item['tags'], start=1):
            global_state.screen_win.addstr(y, props_x, str(i) + ") " + t)
            y += 1
        y += 1


        # TODO: word wrap
        # global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, RW=Related Works, S=Select, ?=Help")


    def get_input(self):
        box = CustomTextbox(self.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR

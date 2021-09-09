#!/usr/bin/env python3

from abc import ABC, abstractmethod

import curses

from dynix_ng.utils.curses.textpad import CustomTextbox
from dynix_ng.utils.curses.print import addstr_x_centered, addstr_rigth_x

import dynix_ng.utils.query.recall as recall

import dynix_ng.state.memory as global_state



# ABSTRACT CLASS

class DynixScreen(ABC):

    def __init__(self):
        pass

    def draw(self):
        pass

    def get_input(self):
        pass

    def refresh(self):
        global_state.screen_win.refresh()
        global_state.inputwin.refresh()

    def handle_user_input(self, user_input, SCREENS):
        pass



# MAIN MENU SCREEN

class WelcomeScreen(DynixScreen):

    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()
        session = global_state.session
        input_prompt = global_state.screen_prompt_list[session.screen_id]

        y = 2

        # welcome banner
        for message in global_state.welcome_message:
            addstr_x_centered(global_state.screen_win, y, message)
        y += 1

        # menu
        i = 1
        menu_start_y = y
        menu_desc_list = list(global_state.screen_list.values())[1:]
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
        prompt_text = " " + input_prompt +  " "
        # prompt_text = " Enter your selection (1-" + str(len(menu_desc_list)) + ") and press <Return> : "
        global_state.screen_win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)

        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "S=Shortcut on, BB=Bulleton Board, ?=Help")


    def get_input(self):
        box = CustomTextbox(global_state.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`
        if user_input != curses.ERR:
            try:
                    return list(global_state.screen_list.keys())[int(user_input)]
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
        session = global_state.session
        desc = global_state.screen_list[session.screen_id]
        input_prompt = global_state.screen_prompt_list[session.screen_id]

        y = 1

        addstr_x_centered(global_state.screen_win, y, desc)
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
        prompt_text = " " + input_prompt +  " "
        global_state.screen_win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)
        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, ?=Help")


    def get_input(self):
        box = CustomTextbox(global_state.inputwin)
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
    def __init__(self):
        session = global_state.session
        session.search_stage = 'count'
        session.search.query_count_incremental()

        super().__init__()


    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()
        session = global_state.session
        input_prompt = global_state.screen_prompt_list[session.screen_id]

        nb_total = str(global_state.session.search.results_total_count)

        y = 1

        global_state.screen_win.addstr(y, 5, " ".join(session.search.recall_query))
        global_state.screen_win.addstr(y, 5 + 20 + 2, "Total=" + nb_total)
        y += 1

        global_state.screen_win.addstr(y, 4, "Searching...                Running Total")
        y += 2

        for term, count in session.search.results_incremental_counts.items():
            global_state.screen_win.addstr(y, 4, term)
            global_state.screen_win.addstr(y, 25, str(count))
            y += 1

        global_state.screen_win.addstr(lines - 7, 4, "titles matched     " + nb_total)

        global_state.screen_win.addstr(lines - 5, 4, "To narrow the search, enter more words.")
        global_state.screen_win.addstr(lines - 4, 4, "Or, press 'D' and <Return> to see all " + nb_total + " titles.")

        # input
        prompt_text = " " + input_prompt +  " "
        global_state.screen_win.addstr(lines - 2, 1, prompt_text, curses.A_STANDOUT)
        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, D=Display, ?=Help")


    def get_input(self):
        box = CustomTextbox(global_state.inputwin)
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

    def __init__(self):
        session = global_state.session
        session.search_stage = 'summary'
        session.search.query()

        super().__init__()

    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()
        session = global_state.session

        pub_date_len = 10
        pub_date_len_w_margin = 15
        normal_margin = 2
        name_l_margin= 6

        y = 1

        # query
        global_state.screen_win.addstr(y, 4, "Your search:  " + ' '.join(session.search.recall_query))
        y += 1

        # table header
        global_state.screen_win.addstr(y, 6, "AUTHOR")
        addstr_x_centered(global_state.screen_win, y, "TITLE")
        global_state.screen_win.addstr(y, cols - pub_date_len_w_margin, "DATE")
        y += 1

        # results table
        i = 1
        for item_id, item in session.search.results.items():
            # author_summary = ' - '.join(item['authors_sorted'])
            res_id_prefix = str(i) + ". "
            author_summary = ' - '.join(item['authors'])
            author_line = res_id_prefix + author_summary
            if len(author_line) > (cols - pub_date_len_w_margin - (normal_margin * 2)):
                author_line = author_line[:(cols - pub_date_len_w_margin - (normal_margin * 2) - 3)] + '...'

            name_line = item['name']
            if len(name_line) > (cols - name_l_margin - pub_date_len_w_margin - normal_margin):
                name_line = name_line[:(cols - name_l_margin - pub_date_len_w_margin - normal_margin) - 3] + '...'

            pub_date = item['pub_date'][:pub_date_len]
            if pub_date == '0101-01-01':
                pub_date = '????'
            # TODO: word wrap
            global_state.screen_win.addstr(y, normal_margin, author_line)
            y += 1
            # global_state.screen_win.addstr(y, 6, title_n_ndate)
            # global_state.screen_win.addstr(y, 6, item['sorted_name'])
            global_state.screen_win.addstr(y, name_l_margin, name_line)
            # global_state.screen_win.addstr(y, 6, item['sorted'])
            global_state.screen_win.addstr(y, cols - pub_date_len_w_margin, pub_date) # TODO: fixme
            i += 1
            y += 1

            if y == lines - 3:
                break

        # paging
        # TODO: right-align
        global_state.screen_win.addstr(lines - 3, 0, "---" + str(session.search.results_total_count) + " titles, End of List" + "---")

        # shortcuts
        global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, D=Display, ?=Help")


    def get_input(self):
        box = CustomTextbox(global_state.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR



# ITEM SCREEN

class ItemScreen(DynixScreen):

    def __init__(self):
        session = global_state.session
        session.search_stage = 'item'
        super().__init__()

    def draw(self):
        (lines, cols) = global_state.screen_win.getmaxyx()
        session = global_state.session

        y = 1

        props_x = 9 + 7 + 2

        # query
        addstr_rigth_x(global_state.screen_win, y, 16, "Call Number:")
        global_state.screen_win.addstr(y, props_x, str(session.item['item_id']))
        y += 2

        addstr_rigth_x(global_state.screen_win, y, 16, "AUTHOR:")

        # for i, a in enumerate(session.item['authors_sorted'], start=1):
        for i, a in enumerate(session.item['authors'], start=1):
            global_state.screen_win.addstr(y, props_x, str(i) + ") " + a)
            y += 1
        y += 1

        addstr_rigth_x(global_state.screen_win, y, 16, "TITLE:")
        # TODO: word wrap
        # global_state.screen_win.addstr(y, props_x, session.item['sorted_name'])
        global_state.screen_win.addstr(y, props_x, session.item['name'])
        y += 2

        # addstr_rigth_x(global_state.screen_win, y, 16, "PUBLISHER:")
        addstr_rigth_x(global_state.screen_win, y, 16, "IMPRINT:")
        global_state.screen_win.addstr(y, props_x, ' - '.join(session.item['publishers']))
        y += 2

        if session.item['subjects']:
            # addstr_rigth_x(global_state.screen_win, y, 16, "TAGS:")
            addstr_rigth_x(global_state.screen_win, y, 16, "SUBJECTS:")
            for i, t in enumerate(session.item['subjects'], start=1):
                global_state.screen_win.addstr(y, props_x, str(i) + ") " + t)
                y += 1
        y += 1


        # TODO: word wrap
        # global_state.screen_win.addstr(lines - 1, 0, "Commands: SO=Start Over, B=Back, RW=Related Works, S=Select, ?=Help")


    def get_input(self):
        box = CustomTextbox(global_state.inputwin)
        user_input = box.edit() # NB: breaks after `HALF_DELAY`

        if user_input != curses.ERR:
            return user_input
        return curses.ERR

#!/usr/bin/env python3

from abc import ABC, abstractmethod

import curses

from dynix_ng.utils.curses.textpad import CustomTextbox
from dynix_ng.utils.curses.print import addstr_x_centered



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



# MAIN MENU

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
            return list(self.screens.keys())[int(user_input)]
            return user_input
        return curses.ERR



# SEARCH MENU

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

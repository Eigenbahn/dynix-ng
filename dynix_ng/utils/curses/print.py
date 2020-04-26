#!/usr/bin/env python3

import math

import curses



def addstr_x_centered(win, y, message, flags=0):
    x = int(math.floor((curses.COLS - len(message)) / 2))
    win.addstr(y, x, message, flags)

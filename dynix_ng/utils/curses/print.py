#!/usr/bin/env python3

import math

import curses



def addstr_x_centered(win, y, message, flags=0):
    x = int(math.floor((curses.COLS - len(message)) / 2))
    win.addstr(y, x, message, flags)


def addstr_rigth_x(win, y, x, message, flags=0):
    left_x = x - len(message)
    win.addstr(y, left_x, message, flags)

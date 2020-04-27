#!/usr/bin/env python3

import curses
import datetime

from dynix_ng.utils.curses.print import addstr_x_centered




def draw_modem_header(win):
    # FDX probably means full duplex
    header_txt = " " * 8 + "FDX" + " " * 4 + "10:32p  22- 48"

    # NB: this -1 should not be needed but doesn't work on a gnome-terminal if not set...
    # works on an actual HW terminal
    # header_txt += " " * (curses.COLS - len(header_txt))
    header_txt += " " * (curses.COLS - len(header_txt) - 1)

    win.addstr(0, 0, header_txt, curses.A_UNDERLINE)


def draw_dynix_header(win, library_name, display_seconds=False):
    now = datetime.datetime.now()
    today_str = now.strftime("%d %b %Y").upper()

    # (curr_locale, curr_encoding) = locale.getlocale()
    # locale.setlocale(locale.LC_CTYPE, 'en_US.utf8')
    time_format = "%I:%M%p"
    if display_seconds:
        time_format = "%I:%M:%S%p"
        now_str = now.strftime(time_format).lower()
        # locale.setlocale(locale.LC_CTYPE, curr_locale + '.' + curr_encoding)

    now_str_modem = now_str[:-1]

    win.addstr(0, 1, " " * (curses.COLS - 2), curses.A_REVERSE)
    win.addstr(0, 2, today_str, curses.A_REVERSE)
    win.addstr(0, curses.COLS - len(now_str) - 2, now_str, curses.A_REVERSE)
    addstr_x_centered(win, 1, library_name, curses.A_REVERSE)

    # addstr_x_centered(stdscr, 1, " Dial Pac ", curses.A_REVERSE)

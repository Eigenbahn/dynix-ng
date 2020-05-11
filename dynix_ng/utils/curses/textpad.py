#!/usr/bin/env python3

import curses
from curses.textpad import Textbox

import dynix_ng.utils.curses.ascii as ascii_ext



# CUSTOM TEXTBOX CLASS

class CustomTextbox(Textbox):
    """Wrapper around `Textbox` widget from curses.textpad.

    Provides a modified `edit()` that takes into account `curses.halfdelay()`.

    Additionnally, enhances text inputs with:
    - extended DEL and BACKSPACE support
    - basic clipboard support
    - extended Emacs keys support

    Here are the added key bindings:

    DEL        Delete character under cursor.
    BACKSPACE  Delete character backward.
    Alt-V      Copy whole line clipboard.
    Ctrl-W     Cut whole line to clipboard.
    Ctrl-X     (same)
    Ctrl-K     Cut end of line to keyboard.
    Ctrl-Y     Paste clipboard.
    Ctrl-C     (same)

    Not working yet:


    See documentation for `Textbox` to see the remaining ones.
    """

    def __init__(self, win, insert_mode=False):
        self.clipboard = ""
        self.is_alt = False
        super().__init__(win, insert_mode)

    def do_command(self, ch):
        "Process a single editing command."
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        # print('---')
        # pprint(ch)
        if ch == ascii_ext.ALT:
            self.is_alt = True
            return 1
        if curses.ascii.isprint(ch) and not self.is_alt:
            if y < self.maxy or x < self.maxx:
                self._insert_printable_char(ch)
        elif ch == curses.ascii.SOH:                           # ^a
            self.win.move(y, 0)
        elif ch in (curses.ascii.STX,
                    curses.KEY_LEFT,
                    curses.ascii.BS,
                    curses.KEY_BACKSPACE, ascii_ext.BACKSPACE):
            if x > 0:
                self.win.move(y, x-1)
            elif y == 0:
                pass
            elif self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
            else:
                self.win.move(y-1, self.maxx)
            if ch in (curses.ascii.BS,
                      curses.KEY_BACKSPACE, ascii_ext.BACKSPACE):
                self.win.delch()
        elif ch in (curses.ascii.EOT,                          # ^d
                    curses.ascii.DEL, ascii_ext.DEL):          # Del
            self.win.delch()
        elif ch == curses.ascii.ENQ:                           # ^e
            if self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            else:
                self.win.move(y, self.maxx)
        elif ch in (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            if x < self.maxx:
                self.win.move(y, x+1)
            elif y == self.maxy:
                pass
            else:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.BEL:                           # ^g
            return 0
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                return 0
            elif y < self.maxy:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.VT:                            # ^k
            self.clipboard_gather(x)
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
        elif ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        elif ch in (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            if y < self.maxy:
                self.win.move(y+1, x)
                if x > self._end_of_line(y+1):
                    self.win.move(y+1, self._end_of_line(y+1))
        elif ch in (curses.ascii.ETB,                          # ^w
                    curses.ascii.CAN):                         # ^x
            self.clipboard_gather()
            self.win.insertln()
            self.win.move(y, 0)
        elif ch == curses.ascii._ctoi("w") and self.is_alt:    # Alt + w
            self.clipboard_gather()
            self.win.move(y, 0)
        elif ch in (curses.ascii.EM,                           # ^y
                    curses.ascii.SYN):                         # ^v
            for ch2 in self.clipboard:
                (y2, x2) = self.win.getyx()
                if y2 < self.maxy or x2 < self.maxx:
                    self._insert_printable_char(ch2)
        elif ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
        elif ch in (curses.ascii.DLE, curses.KEY_UP):          # ^p
            if y > 0:
                self.win.move(y-1, x)
                if x > self._end_of_line(y-1):
                    self.win.move(y-1, self._end_of_line(y-1))

        if self.is_alt and ch != ascii_ext.ALT:
            self.is_alt = False
        return 1

    def clipboard_gather(self, start_x=0):
        self.clipboard = self.gather(start_x)

    def gather(self, start_x=0):
        "Collect and return the contents of the window."
        result = ""
        self._update_max_yx()
        for y in range(self.maxy+1):
            self.win.move(y, 0)
            stop = self._end_of_line(y)
            if stop == 0 and self.stripspaces:
                continue
            for x in range(start_x, self.maxx+1):
                if self.stripspaces and x > stop:
                    break
                result = result + chr(curses.ascii.ascii(self.win.inch(y, x)))
            if self.maxy > 0:
                result = result + "\n"
        return result

    def edit(self, validate=None):
        "Edit in the widget window and collect the results."
        while 1:
            ch = self.win.getch()
            if ch == curses.ERR: # halfdelay
                return curses.ERR
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break
            self.win.refresh()
        value = self.gather()
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.win.insertln()
        self.win.move(y, 0)
        return value

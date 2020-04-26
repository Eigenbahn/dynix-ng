#!/usr/bin/env python3

from os.path import expanduser

import sqlite3



# MAIN CLASS

class CalibreDb():

    def __init__(self, db_path='~/Calibre Library/metadata.db'):
        self.db_path = expanduser(db_path)
        self.cnnx = sqlite3.connect(self.db_path)
        self.cursor = self.cnnx.cursor()

    def __fetch(self, q, fetch_mode='iter'):
        iter = self.cursor.execute(q)
        if fetch_mode == 'first':
            return self.cursor.fetchone()
        elif fetch_mode == 'all':
            return self.cursor.fetchall()
        else:
            return iter


    # -------------------
    # ITEMS

    def book_list(self, fetch_mode='iter', filters=[]):
        q = '''
        SELECT
          id,
          title AS name,
          sort AS sorted_name,
          pubdate AS published_date,
          isbn AS ISBN,
          lccn AS LCCN,
          timestamp AS in_lib_date,
          last_modified AS modif_in_lib_date
        FROM books;'''
        return self.__fetch(q, fetch_mode)

    def author_list(self, fetch_mode='iter', filters=[]):
        q = 'SELECT id, name, sort AS sorted_name FROM authors;'
        return self.__fetch(q, fetch_mode)

    def tag_list(self, fetch_mode='iter', filters=[]):
        q = 'SELECT id, name FROM tags;'
        return self.__fetch(q, fetch_mode)


    # -------------------
    # JOINS

    def authors_for_book(self, book_id, fetch_mode='iter'):
        q = 'SELECT book AS book_id, author AS author_id FROM books_authors_link;'
        return self.__fetch(q, 'all')
        # return self.author_list(fetch_mode, [''])

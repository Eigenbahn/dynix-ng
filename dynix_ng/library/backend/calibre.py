#!/usr/bin/env python3

from os.path import expanduser
import re

import sqlite3

from pprint import pprint


# UTILS


def sqlite3_rx(expr, item):
    return re.match(expr, item, re.IGNORECASE) is not None

def dict_from_sqlite3_row(row):
    return dict(zip(row.keys(), row))


# MAIN CLASS

class CalibreDb():

    def __init__(self, db_path='~/Calibre Library/metadata.db'):
        self.db_path = expanduser(db_path)
        self.cnnx = sqlite3.connect(self.db_path)
        self.cnnx.row_factory = sqlite3.Row
        self.cnnx.create_function("REGEXP", 2, sqlite3_rx)
        self.cursor = self.cnnx.cursor()

    def __fetch(self, q, fetch_mode='iter', fetch_format='k_v'):
        iter = self.cursor.execute(q)
        if fetch_mode == 'first':
            # FIXME: this looks dirty, row object must have a value accessor
            return list(dict(self.cursor.fetchone()).values())[0]
        elif fetch_mode == 'all':
            if fetch_format == 'k_v':
                return [dict(row) for row in self.cursor.fetchall()]
            else:
                # REVIEW: can we reset the self.cnnx.row_factory on the fly to get values directly?
                return list([dict(row) for row in self.cursor.fetchall()]).values()
        else:
            return iter


    # -------------------
    # ITEMS

    def book_list(self, fetch_mode='iter', fetch_format='v', where="",
                  detailed=False):

        order_by = 'b.sort ASC'

        if fetch_format == 'count':
            cols = 'count(1)'
            fetch_mode = 'first'
            detailed = False
            order_by = ''
        else:
            cols = '''
            b.id AS book_id,
            b.title AS name,
            b.sort AS sorted_name,
            b.pubdate AS pub_date,
            b.isbn AS ISBN,
            b.lccn AS LCCN,
            b.timestamp AS in_lib_date,
            b.last_modified AS modif_in_lib_date
            '''
            if detailed:
                cols += ''',
                a.name as author,
                a.sort as author_sorted,
                p.name as publisher,
                s.name as series,
                s.sort as series_sorted,
                t.name as tag
                '''

        where_list = []

        q = 'SELECT ' + cols + ' FROM books AS b'
        if detailed:
            q += ' LEFT JOIN books_publishers_link AS b_p' \
                + ' ON b_p.book = b.id' \
                + ' LEFT JOIN publishers AS p' \
                + ' ON b_p.publisher = p.id'
            q += ' LEFT JOIN books_tags_link AS b_t' \
                + ' ON b_t.book = b.id' \
                + ' LEFT JOIN tags AS t' \
                + ' ON b_t.tag = t.id'
            q += ' LEFT JOIN books_series_link AS b_s' \
                + ' ON b_s.book = b.id' \
                + ' LEFT JOIN series AS s' \
                + ' ON b_s.series = t.id'
            q += ', authors AS a, books_authors_link AS b_a'
            where_joins = [
                'b_a.author = a.id', 'b_a.book = b.id',
            ]
            where_list.append(' AND '.join(where_joins))
        if where:
            where_list.append(where)

        if where_list:
            q += ' WHERE ' + ' AND '.join(where_list)

        if order_by:
            q += ' ORDER BY ' + order_by


        raw_res = self.__fetch(q, fetch_mode, fetch_format)

        if detailed:
            joins = ('author', 'publisher', 'series', 'tag')
            res = {}
            for b_a in raw_res:
                b_id = b_a['book_id']

                cols_to_group = []
                for j in joins:
                    j_sorted = j + '_sorted'
                    if j in b_a:
                        cols_to_group.append(j)
                    if j_sorted in b_a:
                        cols_to_group.append(j_sorted)

                if not b_id in res:
                    res[b_id] = b_a

                    for k in cols_to_group:
                        if k.endswith('_sorted'):
                            k_new = k.replace('_sorted', 's_sorted')
                        else:
                            k_new = k + 's'
                        res[b_id][k_new] = {b_a[k]}
                        del res[b_id][k]
                else:
                    for k in cols_to_group:
                        if k.endswith('_sorted'):
                            k_new = k.replace('_sorted', 's_sorted')
                        else:
                            k_new = k + 's'
                        res[b_id][k_new].add(b_a[k])
            return res

        return raw_res


    def author_list(self, fetch_mode='iter', fetch_format='v', where=""):
        if fetch_format == 'count':
            cols = 'count(1)'
        else:
            cols = 'id, name, sort AS sorted_name'
        q = 'SELECT ' + cols +  ' FROM authors'
        if where:
            q += ' WHERE ' + where
        return self.__fetch(q, fetch_mode, fetch_format)


    def tag_list(self, fetch_mode='iter', fetch_format='v', where=""):
        if fetch_format == 'count':
            cols = 'count(1)'
        else:
            cols = 'id, name'
        q = 'SELECT ' + cols + ' FROM tags;'
        if where:
            q += ' WHERE ' + where
        return self.__fetch(q, fetch_mode, fetch_format)


    # -------------------
    # JOINS

    def authors_for_book(self, book_id, fetch_mode='iter'):
        q = 'SELECT book AS book_id, author AS author_id FROM books_authors_link;'
        return self.__fetch(q, 'all')
        # return self.author_list(fetch_mode, [''])

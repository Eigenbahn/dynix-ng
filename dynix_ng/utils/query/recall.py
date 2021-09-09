#!/usr/bin/env python3



# USER-INPUT -> RECALL

def user_query_to_recall(query):

    query = query.upper()

    # any punctuation (including hyphens) are ignored
    for p in ['-.,;:!']:
        query = query.replace(p, ' ')

    query_terms = list(filter(None, query.split(' ')))

    return query_terms



# RECALL -> DB DIALECT

def recall_to_db_dialect(db, columns, query_terms):
    if db.BACKEND_TYPE == 'sql':
        return recall_to_sql(columns, query_terms, db.BACKEND_DIALECT)
    elif db.BACKEND_TYPE == 'lucene':
        return recall_to_lucene(columns, query_terms)



# RECALL -> LUCENE

def recall_to_lucene(columns, query_terms):
    archive_term_list = []
    for term in query_terms:
        ends_with_s = term[-1] == "S"
        ends_with_apostroph_s = term[-2:] in ("'S", "S'")
        if term[-1] == '?':
            term = term.replace('?', '*')
        elif ends_with_s or ends_with_apostroph_s:
            if ends_with_apostroph_s:
                term = term[-2:]
            else:
                term = term[-1]
        archive_term_list.append(term)
    v_filter = '(' +  ' OR '.join(archive_term_list) + ')'

    archive_query_filters = []
    for column in columns:
        archive_query_filters.append(column + ':' + v_filter)

    return ' OR '.join(archive_query_filters)



# RECALL -> SQL

# https://stackoverflow.com/questions/5071601/how-do-i-use-regex-in-a-sqlite-query

def recall_to_sql(columns, query_terms, sql_dialect):
    (wb_l, wb_r) = sql_dialect_word_boundaries(sql_dialect)
    wc = sql_dialect_word_character(sql_dialect)
    is_case_sensitive = sql_dialect_is_case_sensitive(sql_dialect)

    sql_rx_list = []
    for term in query_terms:
        ends_with_s = term[-1] == "S"
        ends_with_apostroph_s = term[-2:] in ("'S", "S'")

        if term[-1] == '?':
            term = term.replace('?', wc + '*')
            rx = "'.*" + wb_l + term + wb_r + ".*'"
        elif ends_with_s or ends_with_apostroph_s:
            if ends_with_apostroph_s:
                term_no_apostroph = term[-2:]
            else:
                term_no_apostroph = term[-1]
            rx = "'.*" + wb_l + term_no_apostroph +  + "('S|S)" + wb_r + "S?.*'"
        else:
            rx = "'.*" + wb_l + term + wb_r + ".*'"

        sql_rx_list.append(rx)

    sql_query_filters = []
    for column in columns:
        sql_col_filters = []
        if is_case_sensitive:
            column = 'UPPER(' + column + ')'
        for rx in sql_rx_list:
            sql_col_filters.append(column + " REGEXP " + rx)
        sql_query_filters.append('(' + ' AND '.join(sql_col_filters) + ')')

    return ' OR '.join(sql_query_filters)


def sql_dialect_word_boundaries(dialect):
    default_v = (r'\b', r'\b')
    return {
        'sqlite3': (r'\b', r'\b'),
        'mysql': ('[[:<:]]', '[[:>:]]'),
    }.get(dialect, default_v)


def sql_dialect_word_character(dialect):
    default_v = '[A-Z]'
    return {
        'sqlite3': r'\w',
        'mysql': r'\w',
    }.get(dialect, default_v)


def sql_dialect_is_case_sensitive(dialect):
    default_v = True
    return {
        'sqlite3': False,
        'mysql': False,
    }.get(dialect, default_v)

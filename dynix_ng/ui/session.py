#!/usr/bin/env python3

import dynix_ng.utils.query.recall as recall




class DynixSession():
    def __init__(self):

        self.screen_id = 'welcome'
        self.screen = None

        self.user_input = ""

        self.search = None
        self.search_stage = None
        self.item_id = None
        self.item = None


class DynixSearch():
    def __init__(self, user_query, backend, search_type):
        self.user_query = user_query
        self.recall_query = recall.user_query_to_recall(self.user_query)
        self.search_type = search_type
        self.backend = backend
        self.backend_fields = backend.search_type_corresponding_fields(search_type)

        self.results_total_count = 0
        self.results_incremental_counts = {}
        self.results = {}

    def query_count_incremental(self):
        incremental_terms = []
        for term in self.recall_query:
            incremental_terms.append(term)
            where = recall.recall_to_db_dialect(self.backend, self.backend_fields, incremental_terms)
            count = self.backend.item_list(fetch_mode='first', fetch_format='count', where=where)
            self.results_incremental_counts[term] = count

        self.results_total_count = list(self.results_incremental_counts.values())[-1]

    def query(self):
        # TODO: move this outside to be generic
        where = recall.recall_to_db_dialect(self.backend, self.backend_fields, self.recall_query)
        self.results = self.backend.item_list(fetch_mode='all', fetch_format='k_v', where=where, detailed=True)

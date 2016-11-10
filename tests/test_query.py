# -*- coding: utf-8 -*-
import openliveq as olq
import os

class TestQuery(object):

    def test_load(self):
        filepath = os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_queries.tsv")
        qs = []
        with open(filepath) as f:
            for line in f:
                q = olq.Query.readline(line)
                qs.append(q)

        assert qs[0].query_id == 'OLQ-9998'
        assert qs[0].body == '野球'
        assert len(qs) == 2

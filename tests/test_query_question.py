# -*- coding: utf-8 -*-
import openliveq as olq
import os

class TestQueryQuestion(object):

    def test_load(self):
        filepath = os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_query_question.tsv")
        qs = []
        with open(filepath) as f:
            qs = olq.QueryQuestion.load(f)

        assert qs[0].query_id == 'OLQ-9998'
        assert qs[0].question_id == '1167627151'
        assert len(qs) == 4

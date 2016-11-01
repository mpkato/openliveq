# -*- coding: utf-8 -*-
import openliveq as olq
import os
import datetime

class TestQuestion(object):

    def test_load(self):
        filepath = os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_questions.tsv")
        qs = []
        with open(filepath) as f:
            qs = olq.Question.load(f)

        assert qs[0].query_id == 'OLQ-9998'
        assert qs[0].rank == 1
        assert qs[0].question_id == '1167627151'
        assert qs[0].title.startswith("厚生")
        assert qs[0].snippet.startswith("現在")
        assert qs[0].status == '解決済み'
        assert qs[0].updated_at == datetime.datetime(2011, 8, 13, 5, 13, 27)
        assert qs[0].answer_num == 1
        assert qs[0].view_num == 952
        assert qs[0].category == 'ビジネス、経済とお金 > 保険 > 社会保険'
        assert qs[0].question_body.startswith("厚生")
        assert qs[0].best_answer_body.startswith("厚生")

        assert qs[2].query_id == 'OLQ-9999'
        assert qs[2].rank == 2

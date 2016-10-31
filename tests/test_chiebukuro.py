import openliveq as olq
import os
import pytest

class TestChiebukuro(object):

    def test_detail_search(self):
        chie = olq.Chiebukuro(os.environ["YAHOO_CHIEBUKURO_KEY"])
        question_id = "12166167107"
        res = chie.detail_search(question_id)
        assert res["ResultSet"]["Result"]["QuestionId"] == question_id
        raise

    def test_detail_search_failure(self):
        chie = olq.Chiebukuro(os.environ["YAHOO_CHIEBUKURO_KEY"])
        question_id = "12166167107ABC"
        with pytest.raises(olq.ChiebukuroException):
            res = chie.detail_search(question_id)

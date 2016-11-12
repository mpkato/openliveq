import openliveq as olq
import os

class TestClickthrough(object):

    def test_load(self):
        filepath = os.path.join(os.path.dirname(__file__),
            "fixtures", "sample_clickthrough.tsv")
        cs = []
        with open(filepath) as f:
            for line in f:
                c = olq.Clickthrough.readline(line)
                cs.append(c)

        assert cs[0].query_id == 'OLQ-9998'
        assert cs[0].question_id == '1167627151'
        assert cs[0].rank == 1
        assert cs[0].ctr == 0.5
        assert cs[0].male == 0.4
        assert cs[0].female == 0.6
        assert cs[0].a00 == 0.1
        assert cs[0].a10 == 0.1
        assert cs[0].a20 == 0.1
        assert cs[0].a30 == 0.1
        assert cs[0].a40 == 0.1
        assert cs[0].a50 == 0.1
        assert cs[0].a60 == 0.4

        assert cs[2].query_id == 'OLQ-9999'
        assert cs[2].question_id == '1414846259'
        assert cs[2].rank == 2
        assert cs[2].ctr == 0.2
        assert cs[2].male == 0.5
        assert cs[2].female == 0.5
        assert cs[2].a00 == 0.1
        assert cs[2].a10 == 0.1
        assert cs[2].a20 == 0.1
        assert cs[2].a30 == 0.1
        assert cs[2].a40 == 0.2
        assert cs[2].a50 == 0.2
        assert cs[2].a60 == 0.2

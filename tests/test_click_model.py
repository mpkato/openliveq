# -*- coding: utf-8 -*-
import openliveq as olq
import pytest
from math import exp
from .test_base import TestBase
from openliveq.db import SessionContextFactory

class TestClickModel(TestBase):

    def test_predict(self, clickthroughs):
        probs = olq.ClickModel.estimate(clickthroughs)
        assert probs[("OLQ-9998", "1167627151")] == 0.5 / exp(-0.1)
        assert probs[("OLQ-9999", "1328077703")] == 0.5 / exp(-0.1)
        assert probs[("OLQ-9999", "1414846259")] == 0.2 / exp(-0.2)
        assert probs[("OLQ-9999", "1137083831")] == 0.2 / exp(-0.3)
        assert probs[("OLQ-9999", "1348120213")] == 0.1 / exp(-0.4)

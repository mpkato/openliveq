# -*- coding: utf-8 -*-
import openliveq as olq
import pytest
from .test_base import TestBase
from openliveq.db import SessionContextFactory

class TestClickModel(TestBase):

    def test_predict(self, clickthroughs):
        probs = olq.ClickModel.estimate(clickthroughs)
        print(probs)
        raise

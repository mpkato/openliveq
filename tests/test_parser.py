# -*- coding:utf-8 -*-
import pytest
from openliveq.nlp import Parser

class TestParser(object):

    @pytest.fixture
    def parser(self):
        return Parser()

    @pytest.fixture
    def txt(self):
        return "今日は良い天気です"

    def test_parser_unicode(self, parser, txt):
        '''
        Parser.pos_tokenize
        '''
        result = parser.pos_tokenize(txt)
        assert result[1] == ('今日',
            '名詞,副詞可能,*,*,*,*,今日,キョウ,キョー')

    def test_parser_pos_tokenize(self, parser, txt):
        '''
        Parser.pos_tokenize
        '''
        result = parser.pos_tokenize(txt)
        assert result[1] == ('今日',
            '名詞,副詞可能,*,*,*,*,今日,キョウ,キョー')

    def test_parser_stopword_filter(self, parser, txt):
        '''
        Parser.stopword_filter
        '''
        result = parser.stopword_filter(parser.pos_tokenize(txt),
            lambda x: x[0])
        assert result[1] == ('今日',
            '名詞,副詞可能,*,*,*,*,今日,キョウ,キョー')

    def test_parser_noun_filter(self, parser, txt):
        '''
        Parser.noun_filter
        '''
        result = parser.noun_filter(parser.pos_tokenize(txt))
        print(result[1])
        assert result[1][0] == '天気'

    def test_parser_noun_tokenize(self, parser, txt):
        '''
        Parser.noun_parse
        '''
        result = parser.noun_tokenize(txt)
        assert result[1] == '天気'

# -*- coding: utf-8 -*-
import MeCab

class Parser(object):
    CONTENT_POS_PREFIXES = ["形容詞", "名詞", "動詞", "副詞"]

    def __init__(self):
        self.tagger = MeCab.Tagger()
        self.tagger.parse("")

    def word_tokenize(self, sentence):
        '''
        Word tokenization
        '''
        tokens = [w[0] for w in self._mecab_tokenize(sentence)]
        tokens = self.normalize(tokens)
        return tokens

    def noun_tokenize(self, sentence):
        '''
        Extract only nouns
        '''
        tagged_tokens = self.pos_tokenize(sentence)
        nouns = self.noun_filter(tagged_tokens)
        nouns = self.normalize(nouns)
        return nouns

    def content_word_tokenize(self, sentence):
        '''
        Extract only content words
        '''
        tagged_tokens = self.pos_tokenize(sentence)
        content_words = self.content_word_filter(tagged_tokens)
        content_words = self.lemmatize(content_words)
        content_words = self.normalize(content_words)
        return content_words

    def pos_tokenize(self, sentence):
        '''
        Parse sentences and output pos-tagged tokens.
        '''
        return self._mecab_tokenize(sentence)

    def noun_filter(self, tokens):
        '''
        Filter out non-noun tokens (pos starts with 名詞)
        '''
        return [token for token in tokens
            if token[1].startswith('名詞')]

    def content_word_filter(self, tokens):
        '''
        Include function words (pos starts with CONTENT_POS_PREFIXES)
        '''
        return [token for token in tokens
            if any([token[1].startswith(pos)
                for pos in self.CONTENT_POS_PREFIXES])]

    def normalize(self, tokens):
        '''
        Convert tokens to lowercase
        '''
        return [token[0].lower() for token in tokens]

    def lemmatize(self, tokens):
        '''
        Convert tokens to original forms
        '''
        result = []
        for token in tokens:
            w = token[0]
            fs = token[1].split(",")
            if fs[6] != '*':
                w = fs[6]
            result.append((w, token[1]))
        return result

    def _mecab_tokenize(self, sentence):
        '''
        Sentence tokenization
        '''
        node = self.tagger.parseToNode(sentence)
        result = []
        while node:
            result.append((node.surface, node.feature))
            node = node.next
        return result

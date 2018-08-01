from .query import Query
from .question import Question
from .query_question import QueryQuestion
from .clickthrough import Clickthrough
from .db import BULK_RATE, SessionContextFactory

import datetime

class Validation(object):

    @classmethod
    def file_validation(self,
        training_query, test_query,
        training_question, test_question):
        '''
        File Validation
        '''
        # training_query
        print(training_query)
        queries = Query.load(open(training_query))
        assert(len(queries) == 1000)
        assert(queries[345].query_id == 'OLQ-0346')
        assert(queries[345].body == '宮古島')
        assert(queries[831].query_id == 'OLQ-0832')
        assert(queries[831].body == 'プロ野球')

        # test_query
        print(test_query)
        queries = Query.load(open(test_query))
        assert(len(queries) == 1000)
        assert(queries[345].query_id == 'OLQ-1346')
        assert(queries[345].body == '英検準2級')
        assert(queries[831].query_id == 'OLQ-1832')
        assert(queries[831].body == '小島よしお')

        # training_question
        print(training_question)
        qqs = QueryQuestion.load(open(training_question))

        qs = [q for q in qqs if q.query_id == 'OLQ-0001']
        assert(len(qs) == 1000)
        qs = [q for q in qqs if q.query_id == 'OLQ-0023']
        assert(len(qs) in [281, 339])
        qs = [q for q in qqs if q.query_id == 'OLQ-2000']
        assert(len(qs) == 0)

        # test_question
        print(test_question)
        qqs = QueryQuestion.load(open(test_question))

        qs = [q for q in qqs if q.query_id == 'OLQ-0001']
        assert(len(qs) == 0)
        qs = [q for q in qqs if q.query_id == 'OLQ-2000']
        assert(len(qs) == 1000)

    @classmethod
    def db_validation(cls):
        '''
        DB Validation
        '''
        scf = SessionContextFactory()


        # questions
        with scf.create() as session:
            assert(session.query(Question).count() in [1967274, 1971816])

            questions = session.query(Question)\
                .filter(Question.query_id == 'OLQ-0001').all()
            assert(len(questions) == 1000)

            questions = session.query(Question)\
                .filter(Question.query_id == 'OLQ-0023').all()
            assert(len(questions) in [281, 339])

            questions = session.query(Question)\
                .filter(Question.query_id == 'OLQ-2000').all()
            assert(len(questions) == 1000)

            question = session.query(Question)\
                .filter(Question.query_id == 'OLQ-0001',
                Question.question_id == 'q13166161098').first()
            assert(question.rank in [1, 384])
            assert(question.title == 'バイオハザードって設定に無理がない？ ジルもレベッカも月光をピアノで弾い...')
            assert(question.snippet == '''
弾いたけどピアノ弾いたことない人は楽譜見てもチンプンカンプンで弾けないよね？
ジルとレベッカが弾けない人だったら、どうしたんだろうね？
            '''.strip().replace('\n', ' '))
            assert(question.status == '解決済み')
            assert(question.updated_at == datetime.datetime(2016, 11, 13, 3, 35, 34))
            assert(question.answer_num == 1)
            assert(question.view_num == 42)
            assert(question.category == 'エンターテインメントと趣味 > ゲーム')
            assert(question.question_body == '''
バイオハザードって設定に無理がない？
ジルもレベッカも月光をピアノで弾いたけどピアノ弾いたことない人は楽譜見てもチンプンカンプンで弾けないよね？
ジルとレベッカが弾けない人だったら、どうしたんだろうね？
            '''.strip().replace('\n', ' '))
            assert(question.best_answer_body == '''
レベッカもジルも弾けなかった場合は あのゴールドエンブレムがある場所の横はガラス窓になっていて除草剤でプラントを枯らし仮面を取る植物部屋である。
せやから植物部屋に行って窓ガラスを叩き割ればピアノ弾かんでも取れる。 どや？ バイオハザード設定むりないシリーズ もうネタ切れかいな？
            '''.strip().replace('\n', ' '))


        # clickthrough
        with scf.create() as session:
            assert(session.query(Clickthrough).count() in [440163, 436890])
            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-0001').all()
            assert(len(cts) in [254, 195])

            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-1023').all()
            assert(len(cts) == 0)

            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-1999').all()
            assert(len(cts) == 0)

            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-2000').all()
            assert(len(cts) in [474, 387])

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
        assert(len(qs) == 281)
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
            assert(session.query(Question).count() == 1967274)

            questions = session.query(Question)\
                .filter(Question.query_id == 'OLQ-0001').all()
            assert(len(questions) == 1000)

            questions = session.query(Question)\
                .filter(Question.query_id == 'OLQ-0023').all()
            assert(len(questions) == 281)

            questions = session.query(Question)\
                .filter(Question.query_id == 'OLQ-2000').all()
            assert(len(questions) == 1000)

            question = session.query(Question)\
                .filter(Question.query_id == 'OLQ-0001',
                Question.question_id == 'q13166161098').first()
            assert(question.rank == 1)
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


            question = session.query(Question)\
                .filter(Question.query_id == 'OLQ-0002',
                Question.question_id == 'q10150832965').first()
            assert(question.rank == 996)
            assert(question.title == 'チベット学の研究は、せめてよその大学で、地味ぃにしはったらええのに。 だ...')
            assert(question.snippet == '''
だからこその名誉挽回！とかいうのは、それは違う、としか言いようがない。 小説家と親しく話したりするような姿だけで、判断しない方が得策。 なぜなら、めっちゃ怪しいですよ、ダライラマの講演会に来てる、な...
            '''.strip().replace('\n', ''))
            assert(question.status == '解決済み')
            assert(question.updated_at == datetime.datetime(2015, 11, 16, 3, 35, 45))
            assert(question.answer_num == 1)
            assert(question.view_num == 35)
            assert(question.category == '教養と学問、サイエンス > 一般教養')
            assert(question.question_body == '''
チベット学の研究は、せめてよその大学で、地味ぃにしはったらええのに。  だからこその名誉挽回！とかいうのは、それは違う、としか言いようがない。 小説家と親しく話したりするような姿だけで、判断しない方が得策。  なぜなら、めっちゃ怪しいですよ、ダライラマの講演会に来てる、なぞの日本人センセイたち＆お弟子さん。  カタギではないオーラがホントすごくて、びっくりします、実際に見ると。  何年もダラムサラに通っているようなクロアチア人の女性（密教学博士）でも、完全お茶くみやしね。 正式な場では、まだまだ全然、前近代。だから、そういうのが、まだまだ実は当たり前の世界。  「あ、それは言わないで」のアカデミックMYルールは簡単には通用しない、というのだけは、せめて気付いていただきたいです。   アジールとか、河合隼雄≒後白河法皇説とか。そやから、それは単なる中沢新一脳内妄想ネタであって。  オウム事件直後、殊勝らしい内容の文章をいくつか発表しつつ、同時期の別の対談ではこんな感じでした。何にも驚かなかったけど。   浅田「中沢クンの言うことを本気にする人っているんだねぇ」中沢「そうなんですよ、まいっちゃいますよ（笑）」   「５０代（一般）の人々は往々にして、なぜ中沢さんが嫌いなのか？」と、常々疑問に思っている方々への、ひとつの解答として。
            '''.strip().replace('\n', ' '))
            assert(question.best_answer_body == '''
質問ではないのでしょうか
            '''.strip().replace('\n', ' '))

        # clickthrough
        with scf.create() as session:
            assert(session.query(Clickthrough).count() == 440163)
            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-0001').all()
            assert(len(cts) == 254)

            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-1023').all()
            assert(len(cts) == 0)

            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-1999').all()
            assert(len(cts) == 0)

            cts = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-2000').all()
            assert(len(cts) == 474)

            ct = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-0001',
                    Clickthrough.question_id == 'q10155369885').first()
            assert(ct.rank == 196)
            assert(ct.ctr == 0.5)
            assert(ct.male == 1.0)
            assert(ct.female == 0.0)
            assert(ct.a00 == 0)
            assert(ct.a10 == 0)
            assert(ct.a20 == 0)
            assert(ct.a30 == 0)
            assert(ct.a40 == 1.0)
            assert(ct.a50 == 0)
            assert(ct.a60 == 0)

            ct = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-0001',
                    Clickthrough.question_id == 'q10155369885').first()
            assert(ct.rank == 196)
            assert(ct.ctr == 0.5)
            assert(ct.male == 1.0)
            assert(ct.female == 0.0)
            assert(ct.a00 == 0)
            assert(ct.a10 == 0)
            assert(ct.a20 == 0)
            assert(ct.a30 == 0)
            assert(ct.a40 == 1.0)
            assert(ct.a50 == 0)
            assert(ct.a60 == 0)

            ct = session.query(Clickthrough)\
                .filter(Clickthrough.query_id == 'OLQ-1493',
                    Clickthrough.question_id == 'q13163258063').first()
            assert(ct.rank == 1)
            assert(ct.ctr == 0.111)
            assert(ct.male == 1.0)
            assert(ct.female == 0.0)
            assert(ct.a00 == 0)
            assert(ct.a10 == 0)
            assert(ct.a20 == 0)
            assert(ct.a30 == 0)
            assert(ct.a40 == 0)
            assert(ct.a50 == 0)
            assert(ct.a60 == 1)

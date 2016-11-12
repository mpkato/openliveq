from .query import Query
from .question import Question
from .query_question import QueryQuestion
from .clickthrough import Clickthrough
from .collection import Collection
from .feature_factory import FeatureFactory
from .instance import Instance
from .click_model import ClickModel
from .db import BULK_RATE, SessionContextFactory
from collections import defaultdict
import sys, os
import click

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())

@main.command(help='''
    Load data into a SQLite3 database

    \b
    Arguments:
        QUESTION_FILE:     path to the question file
        CLICKTHROUGH_FILE: path to the clickthrough file
''')
@click.argument('question_file', required=True, type=click.File('r'))
@click.argument('clickthrough_file', required=True, type=click.File('r'))
@click.option('--verbose', '-v', is_flag=True, help="increase verbosity.")
def load(question_file, clickthrough_file, verbose):
    print("""
    question_file:     %s
    clickthrough_file: %s
    """ % (question_file.name, clickthrough_file.name, ))

    scf = SessionContextFactory(echo=verbose)

    # questions (bulk insert)
    with scf.create() as session:
        for idx, line in enumerate(question_file):
            elem = Question.readline(line)
            session.add(elem)
            if idx % BULK_RATE == 0:
                session.flush()
        session.commit()

    # clickthroughs (bulk insert)
    with scf.create() as session:
        for idx, line in enumerate(clickthrough_file):
            elem = Clickthrough.readline(line)
            session.add(elem)
            if idx % BULK_RATE == 0:
                session.flush()
        session.commit()

    # report
    with scf.create() as session:
        print("%d questions loaded" % session.query(Question).count())
        print("%d clickthroughs loaded" % session.query(Clickthrough).count())

@main.command(help='''
    Feature extraction from query-question pairs

    \b
    Arguments:
        QUERY_FILE:          path to the query file
        QUERY_QUESTION_FILE: path to the file of query and question IDs
        OUTPUT_FILE:         path to the output file
''')
@click.argument('query_file', required=True, type=click.File('r'))
@click.argument('query_question_file', required=True, type=click.File('r'))
@click.argument('output_file', required=True, type=click.File('w'))
@click.option('--verbose', '-v', is_flag=True, help="increase verbosity.")
def feature(query_file, query_question_file, output_file, verbose):
    print("""
    query_file:          %s
    query_question_file: %s
    output_file:         %s
    """ % (query_file.name, query_question_file.name, output_file.name))

    print("Loading queries and questions ...")
    queries = Query.load(query_file)
    queries = {q.query_id: q for q in queries}
    query_file.close()
    qqs = QueryQuestion.load(query_question_file)
    qqs_per_q = defaultdict(list)
    query_id_index = {}
    for qq in qqs:
        if not qq.query_id in query_id_index:
            query_id_index[qq.query_id] = len(query_id_index)
        qqs_per_q[qq.query_id].append(qq)
    qqs_per_q = sorted(qqs_per_q.items(), 
        key=lambda x: query_id_index[x[0]])
    query_question_file.close()

    ff = FeatureFactory()
    collection = Collection()
    scf = SessionContextFactory(echo=verbose)
    with scf.create() as session:
        for question in session.query(Question):
            ws = ff.parse_question(question)
            collection.add(ws)
    print()

    print("Extracting features ...")
    with scf.create() as session:
        for idx, (query_id, qs) in enumerate(qqs_per_q):
            tmpqid = idx + 1
            instances = []
            for q in qs:
                query = queries[query_id]
                question = session.query(Question).\
                    filter(
                        Question.query_id == query_id,
                        Question.question_id == q.question_id).first()
                if question is None:
                    raise RuntimeError("No such question in DB: %s, %s"
                        % (query_id, q.question_id))
                instance = ff.extract(query, question, collection)
                instances.append(instance)
            Instance.dump(tmpqid, instances, output_file)
    output_file.close()

@main.command(help='''
    Output relevance scores based on a very simple click model

    \b
    Arguments:
        OUTPUT_FILE: path to the output file
''')
@click.argument('output_file', required=True, type=click.File('w'))
@click.option('--sigma', type=float, default=10.0,
    help="used for estimating the examination probability based on the rank.")
@click.option('--max_grade', type=int, default=4,
    help="maximum relevance grade (scores are squashed into [0, max_grade])")
@click.option('--topk', type=int, default=10,
    help="only topk results are used (the default value 10 is highly recommended).")
@click.option('--verbose', '-v', is_flag=True, help="increase verbosity.")
def relevance(output_file, sigma, max_grade, topk, verbose):
    print("""
    output_file: %s
    sigma:       %s
    max_grade:   %s
    topk:        %s
    """ % (output_file.name, sigma, max_grade, topk))

    scf = SessionContextFactory(echo=verbose)
    with scf.create() as session:
        ctrs = session.query(Clickthrough).all()
    res = ClickModel.estimate(ctrs, sigma=sigma, topk=topk)
    res_per_q = defaultdict(list)
    for ids, s in res.items():
        res_per_q[ids[0]].append((ids, s))
    for query_id in sorted(res_per_q):
        scores = [s for ids, s in res_per_q[query_id]]
        max_score = max(scores)
        for ids, s in res_per_q[query_id]:
            score = int(s / max_score * max_grade) # normalization
            output_file.write("\t".join(list(ids) + [str(score)]) + "\n")
    output_file.close()

@main.command(help='''
    Generating training data with feature and relevance files

    \b
    Arguments:
        FEATURE_FILE:   path to the file generated by 'feature'
        RELEVANCE_FILE: path to the file generated by 'relevance'
        OUTPUT_FILE:    path to the output file
''')
@click.argument('feature_file', required=True, type=click.File('r'))
@click.argument('relevance_file', required=True, type=click.File('r'))
@click.argument('output_file', required=True, type=click.File('w'))
def judge(feature_file, relevance_file, output_file):
    print("""
    feature_file:   %s
    relevance_file: %s
    output_file:    %s
    """ % (feature_file.name, relevance_file.name, output_file.name))

    rels = {}
    for line in relevance_file:
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 3:
            raise RuntimeError("Invalid file format: %s" % line)
        rels[tuple(ls[:2])] = ls[-1]
    relevance_file.close()

    for line in feature_file:
        ls = [l for l in line.split(" ")]
        if ls[0] != "0":
            raise RuntimeError("Relevance already exists: %s" % line)
        if not ls[1].startswith("qid"):
            raise RuntimeError("Invalid file format: %s" % line)
        query_id = ls[-2]
        question_id = ls[-1].strip()
        key = (query_id, question_id)
        if key in rels:
            ls[0] = rels[key]
            output_file.write(" ".join(ls))
    feature_file.close()
    output_file.close()

@main.command(help='''
    Ranking test data by scores given by RankLib

    \b
    Arguments:
        FEATURE_FILE: path to the feature file for test data
        SCORE_FILE:   path to the score file generated by RankLib
        OUTPUT_FILE:  path to the output file
''')
@click.argument('feature_file', required=True, type=click.File('r'))
@click.argument('score_file', required=True, type=click.File('r'))
@click.argument('output_file', required=True, type=click.File('w'))
def rank(feature_file, score_file, output_file):
    print("""
    feature_file: %s
    score_file:   %s
    output_file:  %s
    """ % (feature_file.name, score_file.name, output_file.name))

    scores = {}
    for idx, line in enumerate(score_file):
        ls = [l.strip() for l in line.split("\t")]
        if len(ls) != 3:
            raise RuntimeError("Invalid file format: %s" % line)
        scores[idx] = float(ls[-1])
    score_file.close()

    result = defaultdict(list)
    num = 0
    for idx, line in enumerate(feature_file):
        ls = [l for l in line.split(" ")]
        if ls[0] != "0":
            raise RuntimeError("Relevance already exists: %s" % line)
        if not ls[1].startswith("qid"):
            raise RuntimeError("Invalid file format: %s" % line)
        query_id = ls[-2]
        question_id = ls[-1].strip()
        result[query_id].append((question_id, scores[idx]))
        num += 1
    feature_file.close()

    if num != len(scores):
        raise RuntimeError(
            """The number of lines does not match in two input files.""")

    for query_id in sorted(result.keys()):
        ranked = sorted(result[query_id], key=lambda x: x[1], reverse=True)
        ranked = [r[0] for r in ranked]
        for question_id in ranked:
            output_file.write("\t".join((query_id, question_id)) + "\n")
    output_file.close()

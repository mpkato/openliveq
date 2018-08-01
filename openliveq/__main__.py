from .query import Query
from .question import Question
from .query_question import QueryQuestion
from .clickthrough import Clickthrough
from .collection import Collection
from .feature_factory import FeatureFactory
from .instance import Instance
from .click_model import ClickModel
from .db import BULK_RATE, SessionContextFactory
from .validation import Validation
from collections import defaultdict
import sys, os
import click
import requests
import json

FILES = ['OpenLiveQ-queries-train.tsv', 'OpenLiveQ-queries-test.tsv',
    'OpenLiveQ-questions-train.tsv', 'OpenLiveQ-questions-test.tsv']
FILES2 = ['OpenLiveQ2-queries-train.tsv', 'OpenLiveQ2-queries-test.tsv',
    'OpenLiveQ2-questions-train.tsv', 'OpenLiveQ2-questions-test.tsv']

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
    File validation of the OpenLiveQ data

    \b
    Arguments:
        DATA_DIR:          path to the OpenLiveQ data directory
''')
@click.argument('data_dir', required=True, type=str)
def valfiles(data_dir):
    if not os.path.isdir(data_dir):
        print("'%s' does not exist or is not a directory" % data_dir)
        sys.exit(0)
    print(Validation.file_validation.__doc__.strip())

    olq2_flag = False
    for filename in FILES:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            for filename2 in FILES2:
                filepath2 = os.path.join(data_dir, filename2)
                if not os.path.exists(filepath2):
                    print("Neither '%s' nor '%s' exists" % (filepath, filepath2))
                    sys.exit(0)
            olq2_flag = True
            break

    Validation.file_validation(*[os.path.join(data_dir, filename)
        for filename in (FILES2 if olq2_flag else FILES)])
    print('OK')

@main.command(help='''
    DB validation of the OpenLiveQ data
''')
def valdb():
    print(Validation.db_validation.__doc__.strip())
    Validation.db_validation()
    print('OK')

@main.command(help='''
    Parse the entire corpus

    \b
    Arguments:
        OUTPUT_FILE:    path to the output file
''')
@click.argument('output_file', required=True, type=click.File('w'))
@click.option('--verbose', '-v', is_flag=True, help="increase verbosity.")
def parse(output_file, verbose):
    print("""
    output_file:         %s
    """ % output_file.name)

    ff = FeatureFactory()
    collection = Collection()
    scf = SessionContextFactory(echo=verbose)
    with scf.create() as session:
        query_ids = [q[0] for q
            in session.query(Question.query_id).distinct().all()]
        for query_id in query_ids:
            print('\tProcessing questions for query %s' % query_id)
            for question in session.query(Question)\
                .filter(Question.query_id == query_id).all():
                ws = ff.parse_question(question)
                collection.add(ws)
    print()

    collection.dump(output_file)
    output_file.close()
    print("The entire collection has been parsed")
    with open(output_file.name) as f:
        collection = Collection.load(f)
        print("\tThe number of documents: %d" % collection.dn)
        print("\tThe number of unique words: %d" % len(collection.df))
        print("\tThe number of words: %d" % collection.cn)


@main.command(help='''
    Feature extraction from query-question pairs

    \b
    Arguments:
        QUERY_FILE:          path to the query file
        QUERY_QUESTION_FILE: path to the file of query and question IDs
        COLLECTION_FILE:     path to the output file of the 'parse' command
        OUTPUT_FILE:         path to the output file
''')
@click.argument('query_file', required=True, type=click.File('r'))
@click.argument('query_question_file', required=True, type=click.File('r'))
@click.argument('collection_file', required=True, type=click.File('r'))
@click.argument('output_file', required=True, type=click.File('w'))
@click.option('--verbose', '-v', is_flag=True, help="increase verbosity.")
def feature(query_file, query_question_file, collection_file,
    output_file, verbose):
    print("""
    query_file:          %s
    query_question_file: %s
    collection_file:     %s
    output_file:         %s
    """ % (query_file.name, query_question_file.name, collection_file.name,
        output_file.name))

    print("Loading queries and questions ...")
    queries = Query.load(query_file)
    queries = {q.query_id: q for q in queries}
    query_file.close()
    qqs = QueryQuestion.load(query_question_file)
    question_ids = defaultdict(list)
    for qq in qqs:
        question_ids[qq.query_id].append(qq.question_id)
    query_question_file.close()
    print()

    collection = Collection.load(collection_file)
    collection_file.close()
    print("The collection statistics:")
    print("\tThe number of documents: %d" % collection.dn)
    print("\tThe number of unique words: %d" % len(collection.df))
    print("\tThe number of words: %d" % collection.cn)
    print()

    print("Extracting features ...")
    scf = SessionContextFactory(echo=verbose)
    ff = FeatureFactory()
    with scf.create() as session:
        for idx, query_id in enumerate(sorted(queries.keys())):
            print('\tProcessing questions for query %s' % query_id)
            tmpqid = idx + 1
            query = queries[query_id]
            questions = session.query(Question)\
                .filter(Question.query_id == query_id).all()
            questions = {q.question_id: q for q in questions}
            for question_id in question_ids[query_id]:
                if not question_id in questions:
                    raise RuntimeError("No such question in DB: %s, %s"
                        % (query_id, question_id))
                question = questions[question_id]
                instance = ff.extract(query, question, collection)
                Instance.dump(tmpqid, instance, output_file)
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
        for ids, score in res_per_q[query_id]:
            if max_score > 0:
                score = int(score / max_score * max_grade) # normalization
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

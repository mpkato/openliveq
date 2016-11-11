from .query import Query
from .question import Question
from .query_question import QueryQuestion
from .clickthrough import Clickthrough
from .collection import Collection
from .feature_factory import FeatureFactory
from .instance import Instance
from .db import BULK_RATE, SessionContextFactory
from itertools import groupby
import sys, os
import click

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())

@main.command(help='''
    Feature extraction from query-question pairs

    \b
    Arguments:
        QUERY_FILE:             path to the query file
        QUERY_QUESTION_FILE:    path to the file of query and question IDs
        OUTPUT_FILE:            path to the output file
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
    print()

    print("Loading queries and questions ...")
    queries = Query.load(query_file)
    queries = {q.query_id: q for q in queries}
    query_file.close()
    qqs = QueryQuestion.load(query_question_file)
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
        for idx, (query_id, qs) in enumerate(
            groupby(qqs, key=lambda x: x.query_id)):
            tmpqid = idx + 1
            instances = []
            for q in qs:
                query = queries[query_id]
                question = session.query(Question).\
                    filter(
                        Question.query_id == query_id,
                        Question.question_id == q.question_id).first()
                instance = ff.extract(query, question, collection)
                instances.append(instance)
            Instance.dump(tmpqid, instances, output_file)
    output_file.close()

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

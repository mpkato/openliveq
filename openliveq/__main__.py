from .query import Query
from .question import Question
from .clickthrough import Clickthrough
from .collection import Collection
from .feature_factory import FeatureFactory
from .instance import Instance
from .db import BULK_RATE, SessionContextFactory
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
        QUERY_FILE:    path to the query file
        OUTPUT_FILE:   path to the output file
''')
@click.argument('query_file', required=True, type=click.File('r'))
@click.argument('output_file', required=True, type=click.File('w'))
def feature(query_file, output_file):
    print("""
    query_file:     %s
    output_file:    %s
    """ % (query_file.name, output_file.name))
    print()

    print("Loading queries and questions ...")
    queries = Query.load(query_file)
    query_file.close()

    ff = FeatureFactory()
    collection = Collection()
    scf = SessionContextFactory()
    with scf.create() as session:
        for query in queries:
            for question in session.query(Question).\
                filter(Question.query_id == query.query_id):
                ws = ff.parse_question(question)
                collection.add(ws)
    print()

    print("Extracting features ...")
    with scf.create() as session:
        for idx, query in enumerate(queries):
            tmpqid = idx + 1
            instances = []
            for question in session.query(Question).\
                filter(Question.query_id == query.query_id):
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
def load(question_file, clickthrough_file):
    print("""
    question_file:     %s
    clickthrough_file: %s
    """ % (question_file.name, clickthrough_file.name, ))

    scf = SessionContextFactory()

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

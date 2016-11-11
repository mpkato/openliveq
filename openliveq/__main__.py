from .query import Query
from .question import Question
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
    queries = {q.query_id: q for q in queries}
    query_file.close()

    ff = FeatureFactory()
    collection = Collection()
    scf = SessionContextFactory()
    with scf.create() as session:
        for query_id in queries:
            for question in session.query(Question).\
                filter(Question.query_id == query_id):
                ws = ff.parse_question(question)
                collection.add(ws)
    print()

    print("Extracting features ...")
    result = []
    with scf.create() as session:
        for query_id in queries:
            query = queries[query_id]
            for question in session.query(Question).\
                filter(Question.query_id == query_id):
                instance = ff.extract(query, question, collection)
                result.append(instance)
    Instance.dump(result, output_file)
    output_file.close()

@main.command(help='''
    Load data into a SQLite3 database

    \b
    Arguments:
        QUESTION_FILE: path to the question file
''')
@click.argument('question_file', required=True, type=click.File('r'))
def load(question_file):
    print("""
    question_file:  %s
    """ % (question_file.name,))

    scf = SessionContextFactory()

    # questions (bulk insert)
    with scf.create() as session:
        for idx, line in enumerate(question_file):
            elem = Question.readline(line)
            session.add(elem)
            if idx % BULK_RATE == 0:
                session.flush()
        session.commit()

    # report
    with scf.create() as session:
        print("%d questions loaded" % session.query(Question).count())

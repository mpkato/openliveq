from .query import Query
from .question import Question
from .feature_extractor import FeatureExtractor
from .instance import Instance
from .db import BULK_RATE, SessionContextFactory
from sqlalchemy import func
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
        OUTPUT_FILE:   path to the output file
''')
@click.argument('output_file', required=True, type=click.File('w'))
def feature(output_file):
    print("""
    output_file:    %s
    """ % output_file.name)
    print()

    print("Loading queries and questions ...")
    queries = Query.load(query_file)
    questions = Question.load(question_file)
    query_file.close()
    question_file.close()
    print()

    print("Extracting features ...") 
    fe = FeatureExtractor()
    result = fe.extract(queries, questions)
    print()

    print("Dumping features ...")
    Instance.dump(result, output_file)
    output_file.close()

@main.command(help='''
    Load data into a SQLite3 database

    \b
    Arguments:
        QUERY_FILE:    path to the query file
        QUESTION_FILE: path to the question file
''')
@click.argument('query_file', required=True, type=click.File('r'))
@click.argument('question_file', required=True, type=click.File('r'))
def load(query_file, question_file):
    print("""
    query_file:     %s
    question_file:  %s
    """ % (query_file.name, question_file.name))

    scf = SessionContextFactory()

    # queries
    with scf.create() as session:
        for line in query_file:
            elem = Query.readline(line)
            session.add(elem)
        session.commit()

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
        print("%d queries loaded" %
            session.query(func.count('*')).select_from(Query).scalar())
        print("%d questions loaded" %
            session.query(func.count('*')).select_from(Question).scalar())

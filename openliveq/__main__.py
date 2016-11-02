from .query import Query
from .question import Question
from .feature_extractor import FeatureExtractor
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
        QUESTION_FILE: path to the question file
        OUTPUT_FILE:   path to the output file
''')
@click.argument('query_file', required=True, type=click.File('r'))
@click.argument('question_file', required=True, type=click.File('r'))
@click.argument('output_file', required=True, type=click.File('w'))
def feature(query_file, question_file, output_file):
    print("""
    query_file:     %s
    question_file:  %s
    output_file:    %s
    """ % (query_file.name, question_file.name, output_file.name))
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
    for r in result:
        output_file.write(
            "\t".join([r["query_id"], r["question_id"], 
                "\t".join(map(str, r["features"]))]) + "\n"
        )
    output_file.close()

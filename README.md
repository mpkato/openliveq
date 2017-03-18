# openliveq

This is a python package for NTCIR-13 OpenLiveQ ([http://www.openliveq.net/](http://www.openliveq.net/)),
and provides the following utilities:

* Utility classes for handling the OpenLiveQ data
* Feature extraction (e.g. TF-IDF, BM25, and language model)
* Some tools for learning to rank by [RankLib](https://sourceforge.net/p/lemur/wiki/RankLib/)

## Requirements
- Python 3
- MeCab

## Installation
```bash
$ git clone https://github.com/mpkato/openliveq.git
$ cd openliveq
$ python setup.py install
```

## MeCab Installation

MeCab is required to process Japanese texts.

### Ubuntu
```bash
sudo aptitude install -y mecab libmecab-dev mecab-ipadic-utf8
pip install mecab-python3
```

An additional dictionary (mecab-ipadic-neologd) can be installed as follows:
```bash
git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
cd mecab-ipadic-neologd && sudo ./bin/install-mecab-ipadic-neologd -y
sudo sed -i 's/^dicdir.*/dicdir=\/usr\/lib\/mecab\/dic\/mecab-ipadic-neologd/g' /etc/mecabrc
```

## Example

This example extracts features from each query-question pair,
and applies learning to rank based on relevance estimated by a simple click model.

```bash
# install
$ git clone https://github.com/mpkato/openliveq.git
$ cd openliveq
$ python setup.py install

# prepare data (should be provided by the OpenLiveQ organizers)
$ mkdir data
### copy files ###
$ ls data
OpenLiveQ-clickthrough.tsv    OpenLiveQ-queries-train.tsv
OpenLiveQ-questions-test.tsv  OpenLiveQ-queries-test.tsv    OpenLiveQ-question-data.tsv   OpenLiveQ-questions-train.tsv

# load the data into a SQLite3 database
$ openliveq load data/OpenLiveQ-question-data.tsv \
> data/OpenLiveQ-clickthrough.tsv

    question_file:     data/OpenLiveQ-question-data.tsv
    clickthrough_file: data/OpenLiveQ-clickthrough.tsv

1967274 questions loaded
440163 clickthroughs loaded

# data validation
$ openliveq valdb
DB Validation
OK

# file validation
$ openliveq valfiles data
File Validation
data/OpenLiveQ-queries-train.tsv
data/OpenLiveQ-queries-test.tsv
data/OpenLiveQ-questions-train.tsv
data/OpenLiveQ-questions-test.tsv
OK

# parse the entire collection to obtain some statistics such as DF
$ openliveq parse data/OpenLiveQ-collection.json

output_file:         collection.json

...

The entire collection has been parsed
	The number of documents: 1967274
	The number of unique words: 1114773
	The number of words: 250871848    

# extract features from query-question pairs
$ openliveq feature data/OpenLiveQ-queries-train.tsv \
> data/OpenLiveQ-questions-train.tsv \
> data/OpenLiveQ-collection.json \
> data/OpenLiveQ-features-train.tsv

query_file:          data/OpenLiveQ-questions-train.tsv
query_question_file: data/OpenLiveQ-questions-train.tsv
collection_file:     data/OpenLiveQ-collection.json
output_file:         data/OpenLiveQ-features-train.tsv

Loading queries and questions ...

The collection statistics:
	The number of documents: 1967274
	The number of unique words: 1114773
	The number of words: 250871848

Extracting features ...

$ openliveq feature data/OpenLiveQ-queries-test.tsv \
> data/OpenLiveQ-questions-test.tsv \
> data/OpenLiveQ-collection.json \
> data/OpenLiveQ-features-test.tsv

query_file:          data/OpenLiveQ-questions-test.tsv
query_question_file: data/OpenLiveQ-questions-test.tsv
collection_file:     data/OpenLiveQ-collection.json
output_file:         data/OpenLiveQ-features-test.tsv

Loading queries and questions ...

The collection statistics:
	The number of documents: 1967274
	The number of unique words: 1114773
	The number of words: 250871848

Extracting features ...

# estimate relevance based on clickthrough data
$ openliveq relevance data/OpenLiveQ-relevances.tsv

output_file: data/OpenLiveQ-relevances.tsv
sigma:       10.0
max_grade:   4
topk:        10

# integrate relevance scores and features
$ openliveq judge data/OpenLiveQ-features-train.tsv \
> data/OpenLiveQ-relevances.tsv \
> data/OpenLiveQ-features-train-rel.tsv

# use RankLib for learning
$ wget https://sourceforge.net/projects/lemur/files/lemur/RankLib-2.1/RankLib-2.1-patched.jar/download -O RankLib.jar
$ java -jar RankLib.jar \
> -train data/OpenLiveQ-features-train-rel.tsv \
> -save data/OpenLiveQ-model.dat

# use RankLib for ranking
$ java -jar RankLib.jar \
> -load data/OpenLiveQ-model.dat \
> -rank data/OpenLiveQ-features-test.tsv \
> -score data/OpenLiveQ-scores-test.tsv

$ openliveq rank data/OpenLiveQ-features-test.tsv \
> data/OpenLiveQ-scores-test.tsv \
> data/OpenLiveQ-run.tsv

# results
$ cat data/OpenLiveQ-run.tsv
OLQ-9999    1167627151
OLQ-9999    1328077703
...
```


## Tools

``openliveq`` command is available after installation.

### load
```bash
Usage: openliveq load [OPTIONS] QUESTION_FILE CLICKTHROUGH_FILE

  Load data into a SQLite3 database

  Arguments:
      QUESTION_FILE:     path to the question file
      CLICKTHROUGH_FILE: path to the clickthrough file

Options:
  -v, --verbose  increase verbosity.
  --help         Show this message and exit.
```
This command stores question and clickthrough data into a SQLite database at `openliveq/db.sqlite3`.
See our homepage for the file formats: [NTCIR-13 OpenLiveQ](http://www.openliveq.net/).

This step is necesaary before running the other commands, but only once.

### valdb
```bash
Usage: openliveq valdb [OPTIONS]

  DB validation of the OpenLiveQ data

Options:
  --help  Show this message and exit.
```
This command validates question and clickthrough data stored in the SQLite database. This command is optional.

### valfiles
```bash
Usage: openliveq valfiles [OPTIONS] DATA_DIR

  File validation of the OpenLiveQ data

  Arguments:
      DATA_DIR:          path to the OpenLiveQ data directory

Options:
  --help  Show this message and exit.
```
This command validates query and question files in a directory.
This command is optional.

### parse
```bash
Usage: openliveq parse [OPTIONS] OUTPUT_FILE

  Parse the entire corpus

  Arguments:
      OUTPUT_FILE:    path to the output file

Options:
  -v, --verbose  increase verbosity.
  --help         Show this message and exit.
```
This command parses the entire collection to obtain some statistics such as DF,
and store them into `OUTPUT_FILE`.
This command should be executed before `feature` command,
and `OUTPUT_FILE` should be used as an argument for `feature` command.

### feature
```bash
Usage: openliveq feature [OPTIONS] QUERY_FILE QUERY_QUESTION_FILE OUTPUT_FILE

  Feature extraction from query-question pairs

  Arguments:
      QUERY_FILE:          path to the query file
      QUERY_QUESTION_FILE: path to the file of query and question IDs
      COLLECTION_FILE:     path to the output file of the 'parse' command
      OUTPUT_FILE:         path to the output file

Options:
  -v, --verbose  increase verbosity.
  --help         Show this message and exit.
```
This command extracts features from query-question pairs described in `QUERY_QUESTION_FILE` and output the features in `OUTPUT_FILE` in the RankLib format.
See the RankLib website for the file format: [RankLib](https://sourceforge.net/p/lemur/wiki/RankLib/).

This package uses features 1-30 listed in Table 3, [Tao Qin, Tie-Yan Liu, Jun Xu, Hang Li. LETOR: A benchmark collection for research on learning to rank for information retrieval, Information Retrieval, Volume 13, Issue 4, pp. 346-374, 2010.](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/letor3.pdf).
In addition, features include the number of answers given, the number of page views, etc.
See `openliveq/features` for details.

This command does not provide any relevance score for each query-question pair.
Use `relevance` and `judge` commands to add relevance.

### relevance
```bash
Usage: openliveq relevance [OPTIONS] OUTPUT_FILE

  Output relevance scores based on a very simple click model

  Arguments:
      OUTPUT_FILE: path to the output file

Options:
  --sigma FLOAT        used for estimating the examination probability based
                       on the rank.
  --max_grade INTEGER  maximum relevance grade (scores are squashed into [0,
                       max_grade])
  --topk INTEGER       only topk results are used (the default value 10 is
                       highly recommended).
  -v, --verbose        increase verbosity.
  --help               Show this message and exit.
```
This command estimates the relevance of each question based on the clickthrough data and output the relevance in `OUTPUT_FILE`.
The click model used for the relevance estimation is a simplified _position-based model_ (rf. [Click Models for Web Search](http://www.morganclaypool.com/doi/abs/10.2200/S00654ED1V01Y201507ICR043)).
Relevance of each question is estimated as follows:

`Relevance(d_qr) = CTR_qr / exp(- r / sigma)`

where `d_qr` is the `r`-th ranked document for query `q`,
`CTR_qr` is the clickthrough rate of `d_qr`,
and `sigma` is a parameter.
This model assumes that the examination probability only depends on the rank.

`Relevance(d_qr)` is normalized so that the maximum score for a query becomes `scale` option value (default: 4).

The format of each line in the output is:
```
[Query ID]\t[Question ID]\t[Relevance grade]
```

### judge
```bash
Usage: openliveq judge [OPTIONS] FEATURE_FILE RELEVANCE_FILE OUTPUT_FILE

  Generating training data with feature and relevance files

  Arguments:
      FEATURE_FILE:   path to the file generated by 'feature'
      RELEVANCE_FILE: path to the file generated by 'relevance'
      OUTPUT_FILE:    path to the output file

Options:
  --help  Show this message and exit.
```
This command concatenates two files generated by `feature` and `relevance` commands. More specifically, this adds the relevance scores in `RELEVANCE_FILE` to each query-question pair in `FEATURE_FILE`,
and stores the results in `OUTPUT_FILE`.


### rank
```bash
Usage: openliveq rank [OPTIONS] FEATURE_FILE SCORE_FILE OUTPUT_FILE

  Ranking test data by scores given by RankLib

  Arguments:
      FEATURE_FILE: path to the feature file for test data
      SCORE_FILE:   path to the score file generated by RankLib
      OUTPUT_FILE:  path to the output file

Options:
  --help  Show this message and exit.
```
This command ranks questions for each query in `FEATURE_FILE` based on scores in `SCORE_FILE`, and outputs the results in `OUTPUT_FILE`.

`SCORE_FILE` is typically a file generated by RankLib with options '-load', '-score', and '-save'.
The format of each line in `SCORE_FILE` must be:
```
[X]\t[Y]\t[Score]
```
where `[X]` and `[Y]` are not used (assigned by RankLib).
`[Score]` in `i`-th line is simply applied to a query-question pair in `i`-th line, `FEATURE_FILE`.

The format of each line in `OUTPUT_FILE` is:
```
[Query ID]\t[Question ID]
```
where the order represents the ranks of questions for each query.
This format follows the submission format of NTCIR-13 OpenLiveQ,
but note that a description line should be added to the top.
For example, use the following commands before submission:
```
echo "Description of your system. Change me!" > your_result.tsv
cat YOUR_OUTPUT_FILE >> your_result.tsv
```

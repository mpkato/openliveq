CURDIR=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)

URL=https://sourceforge.net/projects/lemur/files/lemur/RankLib-2.1/RankLib-2.1-patched.jar/download
FILENAME=RankLib.jar
wget $URL -O $CURDIR/$FILENAME

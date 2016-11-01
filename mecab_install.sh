#!/bin/bash
# for Mac/Linux

# Install mecab
cd /tmp
wget "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7cENtOXlicTFaRUE" -O mecab-0.996.tar.gz
tar zxfv mecab-0.996.tar.gz
cd mecab-0.996
./configure
make
sudo make install

# load mecab.so
sudo sh -c "echo '/usr/local/lib' >> /etc/ld.so.conf"
sudo ldconfig

# Install mecab-ipadic
cd /tmp
wget "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7MWVlSDBCSXZMTXM" -O mecab-ipadic-2.7.0-20070801.tar.gz
tar zxfv mecab-ipadic-2.7.0-20070801.tar.gz
cd mecab-ipadic-2.7.0-20070801
./configure --with-charset=utf8
make
sudo make install

pip install mecab-python3

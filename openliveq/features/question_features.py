# -*- coding: utf-8 -*-
from math import log
import time

def answer_num(q):
    return q.answer_num

def log_answer_num(q):
    return log(answer_num(q) + 1)

def view_num(q):
    return q.view_num

def log_view_num(q):
    return log(view_num(q) + 1)

def is_open(q):
    return 1.0 if q.status == '回答受付中' else 0.0

def is_vote(q):
    return 1.0 if q.status == '投票受付中' else 0.0

def is_solved(q):
    return 1.0 if q.status == '解決済み' else 0.0

def rank(q):
    return q.rank

def updated_at(q):
    return log(time.mktime(q.updated_at.timetuple()))

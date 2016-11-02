from math import log

def tf_sum(q, d, ff):
    """
    ID 1 for OHSUMED
    """
    result = 0.0
    for w in set(q) & set(d):
        result += d[w]
    return result

def log_tf_sum(q, d, ff):
    """
    ID 2 for OHSUMED
    """
    result = 0.0
    for w in set(q) & set(d):
        result += log(d[w] + 1)
    return result

def norm_tf_sum(q, d, ff):
    """
    ID 3 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    for w in set(q) & set(d):
        result += d[w]
    if dlen > 0:
        result /= dlen
    return result

def log_norm_tf_sum(q, d, ff):
    """
    ID 4 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    for w in set(q) & set(d):
        result += log(float(d[w]) / dlen + 1)
    return result

def idf_sum(q, d, ff):
    """
    ID 5 for OHSUMED
    """
    result = 0.0
    for w in set(q) & set(d):
        result += log(float(ff.dn) / ff.df[w])
    return result

def log_idf_sum(q, d, ff):
    """
    ID 6 for OHSUMED
    """
    result = 0.0
    for w in set(q) & set(d):
        result += log(log(float(ff.dn) / ff.df[w]))
    return result

def icf_sum(q, d, ff):
    """
    ID 7 for OHSUMED
    """
    result = 0.0
    for w in set(q) & set(d):
        result += log(float(ff.dn) / ff.cf[w] + 1)
    return result

def log_tfidf_sum(q, d, ff):
    """
    ID 8 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    for w in set(q) & set(d):
        result += log(float(d[w]) / dlen\
            * log(float(ff.dn) / ff.df[w] + 1))
    return result

def tfidf_sum(q, d, ff):
    """
    ID 9 for OHSUMED
    """
    result = 0.0
    for w in set(q) & set(d):
        result += d[w] * log(float(ff.dn) / ff.df[w])
    return result

def tf_in_idf_sum(q, d, ff):
    """
    ID 10 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    for w in set(q) & set(d):
        result += log(float(d[w]) / dlen\
            * float(ff.dn) / ff.cf[w] + 1)
    return result

def _bm25_idf(w, ff):
    return log((ff.dn - ff.df[w] + 0.5)
        / (ff.df[w] + 0.5))

def bm25(q, d, ff, k1=2.5, b=0.8):
    """
    ID 11 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    for w in set(q) & set(d):
        result += _bm25_idf(w, ff) * d[w] * (k1 + 1)\
            / (d[w] + k1 * (1 - b + b * dlen / ff.avgdlen))
    return result

def log_bm25(q, d, ff, k1=2.5, b=0.8):
    """
    ID 12 for OHSUMED (+1 for log)
    """
    bm = bm25(q, d, ff, k1, b)
    if bm > 0:
        return log(bm + 1.0)
    else:
        return 0.0


def _lm_pwc(w, ff):
    '''
    Add 1 for smoothing
    '''
    return float(ff.cf[w] + 1.0) / (ff.cn + len(ff.df))

def lm_dir(q, d, ff, mu=50.0):
    """
    ID 13 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    qlen = sum(q.values())
    alpha = mu / (dlen + mu)
    for w in set(q):
        pwc = _lm_pwc(w, ff)
        result += log(pwc)
        if w in d:
            pswd = (d[w] + mu * pwc) / (dlen + mu)
            result += log(pswd / (alpha * pwc))
    result += qlen * log(alpha)
    return result

def lm_jm(q, d, ff, Lambda=0.5):
    """
    ID 14 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    qlen = sum(q.values())
    for w in set(q):
        pwc = _lm_pwc(w, ff)
        result += log(pwc)
        if w in d:
            pswd = (1 - Lambda) * d[w] / dlen\
                + Lambda * pwc
            result += log(pswd / (Lambda * pwc))
    result += qlen * log(Lambda)
    return result

def lm_abs(q, d, ff, delta=0.5):
    """
    ID 15 for OHSUMED
    """
    result = 0.0
    dlen = sum(d.values())
    qlen = sum(q.values())
    alpha = delta * len(d) / dlen
    for w in set(q):
        pwc = _lm_pwc(w, ff)
        result += log(pwc)
        if w in d:
            pswd = max([0.0, d[w] - delta]) / dlen\
                + alpha * pwc
            result += log(pswd / (alpha * pwc))
    result += qlen * log(alpha)
    return result

def dlen(q, d, ff):
    return sum(d.values())

def log_dlen(q, d, ff):
    return log(dlen(q, d, ff) + 1)

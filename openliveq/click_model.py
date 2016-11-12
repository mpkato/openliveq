from math import exp

class ClickModel(object):
    '''
    Simple Position-biased Model:
    P(C_r=1) = P(A_r=1|E_r=1)P(E_r=1),
    where
        C_r is click on the r-th document,
        A_r is being attracted by the r-th document, and
        E_r is examination of the r-th document.

    In this simple model, the examination probability is defined as
    P(E_r=1) = exp(- r / sigma).
    Therefore, P(A_r=1|E_r=1) = P(C_r=1) / P(E_r=1).

    '''
    @classmethod
    def estimate(cls, ctrs, sigma=10.0, topk=10):
        result = {}
        for ctr in ctrs:
            eprob = cls._eprob(ctr.rank, sigma)
            aprob = min([1.0, ctr.ctr / eprob])
            result[(ctr.query_id, ctr.question_id)] = aprob
        return result

    @classmethod
    def _eprob(cls, rank, sigma):
        return exp(- float(rank) / sigma)

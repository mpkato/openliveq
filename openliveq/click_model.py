import random
from collections import defaultdict

class ClickModel(object):
    '''
    I WAS STUPID!!!! THIS IS WRONG!!!!
    Position-biased Model:
    P(C=1) = P(A=1|E=1)P(E=1)
    P(C=0) = P(A=0|E=1)P(E=1) + P(E=0)

    EM algorithm (simplified):
        a_qd = CTR_qd + (1 - CTR_qd) * (1 - g_r) * a_qd / (1 - g_r * a_qd)

        g_r = 1 / Q * SUM (
        CTR_qd + (1 - CTR_qd) * (1 - a_qd) * g_r / (1 - g_r * a_qd))

        where a_qd = P(A=1|E=1) and g_r = P(E=1)
    '''
    @classmethod
    def estimate(cls, ctrs, topk=10, iteration=100, epsilon=1e-5):
        rank_probs = [random.random() for i in range(topk)]
        rel_probs = defaultdict(dict)
        rctrs = defaultdict(list)
        qctrs = defaultdict(list)
        for ctr in ctrs:
            if ctr.rank <= topk:
                rel_probs[ctr.query_id][ctr.question_id] = random.random()
                rctrs[ctr.rank].append(ctr)
                qctrs[ctr.query_id].append(ctr)

        for i in range(iteration):
            prev = list(rank_probs)
            cls._update_rank_probs(rctrs, rank_probs, rel_probs)
            cls._update_rel_probs(qctrs, rank_probs, rel_probs)
            if cls._l2_loss(prev, rank_probs) < epsilon:
                break

        return rel_probs

    @classmethod
    def _update_rank_probs(cls, rctrs, rank_probs, rel_probs):
        for r in rctrs:
            res = 0.0
            for ctr in rctrs[r]:
                alpha = rel_probs[ctr.query_id][ctr.question_id]
                res += ctr.ctr + (1.0 - ctr.ctr)\
                    * (1.0 - alpha) * rank_probs[r]\
                    / (1.0 - alpha * rank_probs[r])
            res /= len(rctrs[r])
            rank_probs[r] = res

    @classmethod
    def _update_rel_probs(cls, qctrs, rank_probs, rel_probs):
        for query_id in qctrs:
            for ctr in qctrs[query_id]:
                alpha = rel_probs[query_id][ctr.question_id]
                rel_probs[query_id][ctr.question_id] = ctr.ctr\
                    + (1.0 - ctr.ctr) * (1.0 - rank_probs[ctr.rank]) * alpha\
                    / (1.0 - alpha * rank_probs[ctr.rank])

    @classmethod
    def _l2_loss(cls, x, y):
        return sum([(xv - yv) ** 2 for xv, yv in zip(x, y)])

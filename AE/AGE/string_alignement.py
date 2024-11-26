# An algorithm to score sequence alignement

import numpy as np
seed = 0
rng = np.random.default_rng(seed)


ga = list(range(20))

# Naive SW algorithm
# Scoring system
score_list = [5, 2, 1, 0, -1, -2, -5] + [-5] * int(len(ga) - 13) + [-5, -2, -1, 0, 1, 2]
score_matrix = np.array(score_list)[np.abs([[(i - j) for j in range(len(ga))] for i in range(len(ga))])]

gap = -3

def naive_scoring(n, sc_list = score_list): # score based on distance
    return sc_list[n]

def lookup_matrix_scoring(c1, c2):
    return score_matrix[c1, c2]

alignement_history = dict()

# S1 and S2 are iterables of which elements can be compared
# s1 == s2 is not checked for because it is assumed to be a very rare case
def order_sequences(s1, s2):
    for i in range(min(len(s1), len(s2))):
        if s1[i] == s2[i]:
            continue
        elif s1[i] < s2[i]:
            return s1, s2
        else:
            return s2, s1
    if len(s1) < len(s2):
        return s1, s2
    else: # either s2 is shorter or s1 == s2
        return s2, s1


def score_alignement_with_history(seq1, seq2, gap = -3, history = alignement_history):

    seq1, seq2 = order_sequences(seq1, seq2)

    seq1, seq2 = tuple(seq1), tuple(seq2)
 
    if (seq1, seq2) in history.keys(): 
        result = history[(seq1, seq2)]['result']
        history[(seq1, seq2)]['count'] += 1
    else:
        result = score_alignement(seq1, seq2, gap = gap)
        history[(seq1, seq2)] = {'result' : result, 'count' : 1}
    return result


def score_alignement(seq1, seq2, gap = -3):

    SW_nmatrix = np.zeros((len(seq1)+1, len(seq2)+1))
    SW_pmatrix = np.zeros((len(seq1)+1, len(seq2)+1, 2), dtype = int)
    for i in range(len(seq1)):
        for j in range(len(seq2)):
            top = SW_nmatrix[i, j + 1] + gap
            left = SW_nmatrix[i+1, j] + gap
            diag = SW_nmatrix[i, j] + lookup_matrix_scoring(seq1[i], seq2[j])

            if diag >= top:
                if diag >= left:
                    SW_nmatrix[i+1, j+1] = diag
                    SW_pmatrix[i+1, j+1] = (i, j)
                else:
                    SW_nmatrix[i+1, j+1] = left
                    SW_pmatrix[i+1, j+1] = (i+1, j)
            elif top > left:
                SW_nmatrix[i+1, j+1] = top
                SW_pmatrix[i+1, j+1] = (i, j+1)
            else:
                SW_nmatrix[i+1, j+1] = left
                SW_pmatrix[i+1, j+1] = (i+1, j)

    start = np.array(np.unravel_index(np.argmax(SW_nmatrix), SW_nmatrix.shape), dtype = int)
    alignment = [start]
    current = start + 0

    while True:
        if SW_nmatrix[(*current,)] == 0:
            break
        else:
            current = SW_pmatrix[(*current,)]
            alignment.append(current)


    return alignment, (SW_nmatrix[(*alignment[0],)])


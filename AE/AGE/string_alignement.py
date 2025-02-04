# An algorithm to score sequence alignement

import numpy as np
import copy as cp
seed = None
rng = np.random.default_rng(seed)


ga = list(range(20))

# Easy complementary sequences
def complement_sequence(sq):
    half_alphabet_size = int(len(ga)/2)
    sq_comp = [ga[(char) - half_alphabet_size] for char in sq]
    return sq_comp

# Determines if there exists a substring of s1 and s2 with exacti matching
def exact_matching(s1, s2, size = 2):
    for i in range(len(s1) - size):
            for j in range(len(s2) - size):
                if np.all([c1 == c2 for c1, c2 in zip(s1[i:i+size],s2[j:j+size])]):
                    return True
    return False

# optimized exact matching

# get lengths of True sequences in an array
def length_of_True(arr):
    if len(arr) == 0:
        return [0]
    sw = (arr[:-1] ^ arr[1:])  # derivate the bools
    isw = np.arange(len(sw))[sw] # where do we change from true to false
    if arr[0]:
        if arr[-1]:
            isw = np.concatenate(([-1], isw, [len(sw)]))
            lens = isw[1::2] - isw[::2]
        else:
            isw = np.concatenate(([-1], isw))
            lens = isw[1::2] - isw[::2]
    elif arr[-1]:
        isw = np.concatenate((isw, [len(sw)]))
        lens = isw[1::2] - isw[::2]
    
    else:
        lens = isw[1::2] - isw[::2]

    return lens

def opti_exact_matching(s1, s2, size = 2):
    s1, s2 = np.broadcast_arrays(np.array(s1).reshape(len(s1), 1), np.array(s2).reshape(1, len(s2)))
    F = s1 == s2

    F_diagonal_lens = [length_of_True(np.diagonal(F, k)) 
                                      for k in range(-F.shape[0] + 1, F.shape[1])
                                      if min(F.shape[1] - k, F.shape[0] + k) >= size]  # diagonals shorter than size cannot contain exact matches

    if F_diagonal_lens:
        return (np.concatenate(F_diagonal_lens) >= size).any()
    else:
        return False
# Naive SW algorithm
# Scoring system
score_list = [5, 2, 1, 0, -1, -2, -5] + [-5] * int(len(ga) - 13) + [-5, -2, -1, 0, 1, 2]
score_matrix = np.array(score_list)[np.abs([[(i - j) for j in range(len(ga))] for i in range(len(ga))])]

gap = -3

def naive_scoring(n, sc_list = score_list): # score based on distance
    return sc_list[n]

def numpy_compliant_naive_scoring(n, sc_list = np.array(score_list)):
    return sc_list[n]

def expert_scoring_for_multi_align_cross(d):
    return np.clip(5 - d, a_min = -5)

def lookup_matrix_scoring(c1, c2):
    return score_matrix[c1, c2]

# padding should never be a possible character !

def scoring_multi_align(characters, c_ref, padding = np.nan):
    scores = np.zeros_like(characters)
    distance = np.zeros_like(characters, dtype = int)
    if padding is np.nan:
        try:
            padding_mask = np.isnan(characters)
        except:
            print(characters, characters.dtype)
            raise
    else:
        padding_mask = (characters == padding)
    distance[np.logical_not(padding_mask)] = characters[np.logical_not(padding_mask)] - c_ref
    try:
        scores[np.logical_not(padding_mask)] = numpy_compliant_naive_scoring(distance[np.logical_not(padding_mask)])
    except:
        print(distance)
        print(padding_mask)
        print(characters[np.logical_not(padding_mask)])
        print(c_ref)
        
        raise
    scores[padding_mask] -= np.inf

    return scores


def scoring_multi_align_cross(chars1, chars2, padding = np.nan):
    c1 = np.reshape(chars1, (len(chars1), 1))
    c2 = np.reshape(chars2, (1, len(chars2)))

    scores = np.zeros((chars1.shape[0], chars2.shape[1]))

    distance = np.zeros_like(scores, dtype = int)
    if padding is np.nan:
        try:
            padding_1 = np.isnan(chars1)
            padding_2 = np.isnan(chars2)
        except:
            print(chars1, chars2, chars1.dtype, chars2.dtype)
            raise
    else:
        padding_1 = (chars1 == padding)
        padding_2 = (chars2 == padding)
    distance[np.logical_not(padding_1), np.logical_not(padding_2)] = c1[np.logical_not(padding_1)] - c2[:, np.logical_not(padding_2)]
    try:
        scores[np.logical_not(padding_1), np.logical_not(padding_2)] = numpy_compliant_naive_scoring(distance[np.logical_not(padding_1), np.logical_not(padding_2)])
    except:
        print(distance)
        print(padding_1)
        print(padding_2)
        print(c1[np.logical_not(padding_1)])
        print(c2[:, np.logical_not(padding_2)])
        
        raise
    scores[padding_1] -= np.inf
    scores[:,padding_2] -= np.inf
    

    return scores


alignement_history = {'use_count' : 0}

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

    hus = history['use_count']
    history['use_count'] = hus + 1
 
    if (seq1, seq2) in history.keys(): 
        result = history[(seq1, seq2)]['result']
        history[(seq1, seq2)]['count'] += 1
    else:
        result = score_alignement(seq1, seq2, gap = gap)
        history[(seq1, seq2)] = {'result' : result, 'count' : 1}
    return result

def score_alignement_with_silencing(seq1, seq2, gap = -3):
    silence = False
    complementary_seq2 = complement_sequence(seq2)
    # Check if there is a 5 - character exact matching between seq1 and comp(seq2)
    silence = opti_exact_matching(seq1, complementary_seq2, size = 5)

    if silence:
        return None, min(score_list)
    # No inhibition
    else:
        return score_alignement(seq1, seq2, gap)


def score_alignement_with_history_and_silencing(seq1, seq2, gap = -3, history = alignement_history):
    seq1, seq2 = order_sequences(seq1, seq2)

    seq1, seq2 = tuple(seq1), tuple(seq2)
 
    if (seq1, seq2) in history.keys(): 
        result = history[(seq1, seq2)]['result']
        history[(seq1, seq2)]['count'] += 1
    else:
        result = score_alignement_with_silencing(seq1, seq2, gap = gap)
        history[(seq1, seq2)] = {'result' : result, 'count' : 1}
    return result


def score_alignement(seq1, seq2, gap = -3):
    # nmatrix for value of current alignement 
    SW_nmatrix = np.zeros((len(seq1)+1, len(seq2)+1))
    # pmatrix for origin of current alignement (last step on path)
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

def score_n_alignment_to_ref(seqs_to_align, seq_ref, gap = -3, padding = np.nan):
# Seqs to align is a Nd array (N >= 2) where items are characters; 'padding' parameter is used to align all sequences to the same length
# This algorithm will not return alignments, only scores
    # Turn seqs_to_align into a list of the nth character in each sequence
    chars_to_align = seqs_to_align.T

    SW_nmatrix = np.zeros((chars_to_align.shape[0] +1, len(seq_ref)+1, *chars_to_align.shape[1:]))
    SW_pmatrix = np.zeros((chars_to_align.shape[0] +1, len(seq_ref)+1, *chars_to_align.shape[1:], 2), dtype = int)

    diag_p = np.zeros(2)
    top_p = np.array([0, 1])
    left_p = np.array([1, 0])
    stop_p = diag_p * np.nan   # ?
    # To make sure we don't get a thousand runtime warnings when np.nan gets multiplied
    np.seterr(invalid = 'ignore')
    for i in range(chars_to_align.shape[0]):
        for j in range(len(seq_ref)):
            top = SW_nmatrix[i, j + 1] + gap
            left = SW_nmatrix[i+1, j] + gap
            diag = SW_nmatrix[i, j] + scoring_multi_align(chars_to_align[i], seq_ref[j], padding = padding)

            diag_is_greater = np.logical_and(diag > 0, np.logical_and(diag >= top, diag >= left))
            top_is_greater = np.logical_and(top > 0, np.logical_and(top > diag, top >= left))
            left_is_greater = np.logical_and(left > 0, np.logical_and(np.logical_not(diag_is_greater), np.logical_not(top_is_greater)))
            zero_is_greater = np.logical_and(np.logical_and(diag <= 0, top <= 0), left <= 0)

            SW_nmatrix[i+1, j+1] = (diag * diag_is_greater + top * top_is_greater + left * left_is_greater)
            # SW_pmatrix[i+1, j+1] = (np.array([i, j]) + diag_p * diag_is_greater + top_p * top_is_greater + left_p * left_is_greater) * (not zero_is_greater)

    np.nan_to_num(SW_nmatrix, False)
    score = np.max(SW_nmatrix, axis = (0, 1)).T  # undoing the first step with .T
    assert (score >= 0).all()
    # Resetting it for warnings elsewhere in the code
    np.seterr(invalid = 'print')

    # Depends on np.argmax(axis = (axes,)) working the same way as np.max(axis = (axes,)) to go fast; 
    # as for now alignement per se is useless, i'll wait on the resolution of https://github.com/numpy/numpy/issues/25623

    
    # Only works if only one last thingy
    if False :
        start_arg = np.argmax(np.argmax(SW_nmatrix, axis = 0), axis = 0).reshape(1, 1, 10)
        print(start_arg.shape, SW_pmatrix[:,:,:,0].shape)
        start = np.take_along_axis(SW_pmatrix[:,:,:,0], start_arg, axis =-1)
        alignment = [start]
        current = start + 0
        last = start + 0

        Done = False * np.zeros_like(start)
        c = 0
        while c < 10 and not Done.all():
            # print(current)
            current = SW_pmatrix[:,:,current,:]
            print(SW_nmatrix[current].shape)
            Done[SW_nmatrix[current] == 0] *= True
            last = cp.copy(current)
            last[Done] *= np.nan
            alignment.append(last)
            c += 1
        print('Done !')
        del alignment
        del SW_pmatrix


        # if SW_nmatrix[(*current,)] == 0:
            # break
        # else:
            # current = SW_pmatrix[(*current,)]
            # alignment.append(current)


    return None, score   # keep the same signature as if alignement was computed !


def score_n_alignment_to_m(seqs1_to_align, seqs2_to_align, gap = -3, padding = np.nan):
# Seqs to align is a 2d array where items are characters; 'padding' parameter is used to align all sequences to the same length
# This algorithm will not return alignments, only scores
    # Turn seqs_to_align into a list of the nth character in each sequence
    chars1_to_align = seqs1_to_align.T
    chars2_to_align = seqs2_to_align.T

    SW_nmatrix = np.zeros((chars_to_align.shape[0] +1, len(seq_ref)+1, *chars_to_align.shape[1:]))
    SW_pmatrix = np.zeros((chars_to_align.shape[0] +1, len(seq_ref)+1, *chars_to_align.shape[1:], 2), dtype = int)

    diag_p = np.zeros(2)
    top_p = np.array([0, 1])
    left_p = np.array([1, 0])
    stop_p = diag_p * np.nan   # ?
    # To make sure we don't get a thousand runtime warnings when np.nan gets multiplied
    np.seterr(invalid = 'ignore')
    for i in range(chars_to_align.shape[0]):
        for j in range(len(seq_ref)):
            top = SW_nmatrix[i, j + 1] + gap
            left = SW_nmatrix[i+1, j] + gap
            diag = SW_nmatrix[i, j] + scoring_multi_align(chars1_to_align[i], chars2_to_align[j], padding = padding)

            diag_is_greater = np.logical_and(diag > 0, np.logical_and(diag >= top, diag >= left))
            top_is_greater = np.logical_and(top > 0, np.logical_and(top > diag, top >= left))
            left_is_greater = np.logical_and(left > 0, np.logical_and(np.logical_not(diag_is_greater), np.logical_not(top_is_greater)))
            zero_is_greater = np.logical_and(np.logical_and(diag <= 0, top <= 0), left <= 0)

            SW_nmatrix[i+1, j+1] = (diag * diag_is_greater + top * top_is_greater + left * left_is_greater)
            # SW_pmatrix[i+1, j+1] = (np.array([i, j]) + diag_p * diag_is_greater + top_p * top_is_greater + left_p * left_is_greater) * (not zero_is_greater)

    np.nan_to_num(SW_nmatrix, False)
    score = np.max(SW_nmatrix, axis = (0, 1)).T  # undoing the first step with .T
    assert (score >= 0).all()
    # Resetting it for warnings elsewhere in the code
    np.seterr(invalid = 'print')

    # Depends on np.argmax(axis = (axes,)) working the same way as np.max(axis = (axes,)) to go fast; 
    # as for now alignement per se is useless, i'll wait on the resolution of https://github.com/numpy/numpy/issues/25623

    
    # Only works if only one last thingy
    if False :
        start_arg = np.argmax(np.argmax(SW_nmatrix, axis = 0), axis = 0).reshape(1, 1, 10)
        print(start_arg.shape, SW_pmatrix[:,:,:,0].shape)
        start = np.take_along_axis(SW_pmatrix[:,:,:,0], start_arg, axis =-1)
        alignment = [start]
        current = start + 0
        last = start + 0

        Done = False * np.zeros_like(start)
        c = 0
        while c < 10 and not Done.all():
            # print(current)
            current = SW_pmatrix[:,:,current,:]
            print(SW_nmatrix[current].shape)
            Done[SW_nmatrix[current] == 0] *= True
            last = cp.copy(current)
            last[Done] *= np.nan
            alignment.append(last)
            c += 1
        print('Done !')
        del alignment
        del SW_pmatrix


        # if SW_nmatrix[(*current,)] == 0:
            # break
        # else:
            # current = SW_pmatrix[(*current,)]
            # alignment.append(current)


    return None, score   # keep the same signature as if alignement was computed !











def many_exact_matching_with_nan_padding(sequences_1, sequences_2, 
                                         n_valid_match, d_substition_to_score_map = lambda d : 1*(d == 0)):

    # two subsequences of size n match ioi at most n characters totalize a score of s through the d map

    # build distance map
    s1 = np.reshape(sequences_1, list(sequences_1.shape) + [1])
    s2 = np.reshape(sequences_2, list(sequences_2.shape) + [1])
    distance_characterwise = (s1 - s2.T)  # propagate nan for now
    # apply substitution map
    score_characterwise = d_substition_to_score_map(distance_characterwise.astype(float ))


    ss_length = np.zeros((s1.shape[0], s2.shape[0]))
    temp_interaction_score = np.zeros_like(ss_length)
    interaction_score = np.zeros_like(ss_length) * np.nan
    for char_score_list in score_characterwise.swapaxes(0, 1):
        # Check is match or not match
        is_nan = np.isnan(char_score_list)
        # where not match --> subsequence length is 0
        ss_length[is_nan] = 0
        # where match --> subsequence length progresses
        ss_length[np.logical_not(is_nan)] += 1
        # store subsequence interaction score
        temp_interaction_score[np.logical_not(is_nan)] += char_score_list[np.logical_not(is_nan)]
        # reset when subsequence stops
        temp_interaction_score[is_nan] = 0
        # when subsequence length reaches limit, add ss interaction score
        interaction_score[ss_length == n_valid_match] = temp_interaction_score[ss_length == n_valid_match]
        # whenever it progresses afterwards, just update it
        interaction_score[ss_length > n_valid_match] += char_score_list[ss_length > n_valid_match]



    return interaction_score 

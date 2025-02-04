from string_alignement import *
from functools import partial
from multiprocessing import Pool, Manager
from matplotlib import pyplot as plt

from scipy.stats import gaussian_kde
from time import time as time
from itertools import cycle

WIP = True
rng = np.random.default_rng()

# letter distance is algebric
def score_matrix_distance_thing_16_january(letter_distance, a):
    letter_distance[np.abs(letter_distance)  > a] = np.nan
    d_sign = np.sign(letter_distance)
    score = d_sign*np.power(2, d_sign * letter_distance)

    return score


def substitute(seqs, p_sub = .1):
    where_to = rng.choice([True, False], p = [p_sub, 1 - p_sub], size = seqs.shape)
    new = rng.choice(genetic_alphabet, size = seqs.shape)
    seqs[where_to] = new[where_to]
# For insert, the considered fixed size means shifting and replacing
def insert(seqs, p_sub = .1, padding = np.nan):
    where_to = rng.choice([True, False], p = [p_sub, 1 - p_sub], size = seqs.shape)
    new = rng.choice(genetic_alphabet, size = where_to.sum())
    c = 0
    for i in range(len(seqs)):
        if where_to[i].any():
            for j in np.argwhere(where_to[i])[::-1, 0]:
                seqs[i, j+1:] = seqs[i, j:-1]
                seqs[i, j] = new[c]
                c += 1
# For delete, the considered fixed size means shifting and adding a NaN at the end
def delete(seqs, p_sub = .1):
    where_to = rng.choice([True, False], p = [p_sub, 1 - p_sub], size = seqs.shape)
    for i in range(len(seqs)):
        if where_to[i].any():
            k = 0
            for j in np.argwhere(where_to[i])[::-1, 0]:
                seqs[i, j:-1] = seqs[i, j+1:]
                seqs[i, -k] = np.nan
                k += 1


# Generate random sequences
# genetic_alphabet = np.array(list(range(20)), dtype = float)
genetic_alphabets = [np.array(list(range(i)), dtype = float) for i in [20]]#[12, 16, 20, 24]]
genetic_alphabet = np.array(list(range(20)), dtype = float)
n_random_sq = 200
N_to_match = np.linspace(0, 10, 11).astype(int, casting='unsafe')
n_to_match = 4

# min_miniseq_size = 4
matching_type = 'subsequence'  #'random'

#sizes_sq =  [5, 10, 15, 20]
size_sq = 40

p_muts = np.geomspace(.0001, .1, 1000)
mutations = [substitute, insert, delete]
mutation = substitute

linestyles = cycle(['solid', 'dashed', '-.'])
linestyle = 'solid'
markers = cycle(['o', '+', 'v'])
marker = 'o'
plt.rcParams['font.size'] = 20
fig, axes = plt.subplots(1, 3, figsize = (20, 20),sharey = 'all', subplot_kw={'xscale' : 'log', 'ylim' : (0.0, 1.0)})
# fig.supylabel("Score's probability for two random sequences")
# fig.supxlabel("Matching score (non-matching interactions are not represented)")
fig.supylabel("Probability for an interaction to be affected by the mutation")
fig.supxlabel("Probability of mutation")

rv_ax = cycle(np.ravel(axes))
ax = axes
# assert len(rv_ax) >= len(sizes_sq)
t0 = time()
for genetic_alphabet in genetic_alphabets:
    a = len(genetic_alphabet)/4
    distance_func = partial(score_matrix_distance_thing_16_january, a = a)


    if matching_type != 'subsequence':
        max_miniseq_size = size_sq + 0

# --- For proportion of matches in random sequences
#     matchs = [np.isnan(many_exact_matching_with_nan_padding(sequences_1, sequences_2, 
#                                                           n_to_match, 
#                                                           distance_func)).sum()/(n_random_sq**2)
#                 for n_to_match in N_to_match]

#     ax.plot(N_to_match, 1 - np.array(matchs), label = f'A = {len(genetic_alphabet)}')
# plt.xlabel('Threshold')
# plt.ylabel('Probability of match')
# plt.legend()
# if False:
# --------------------------------------------------

# --- For connections with mutations
    for mutation in mutations:
        ax = next(rv_ax)
        result = np.zeros((p_muts.shape[0], 3))
        # linestyle = next(linestyles)
        # marker = next(markers)
        for i, p_mut in enumerate(p_muts):
            sequences_1 = rng.choice(genetic_alphabet, size = (n_random_sq, size_sq))
            sequences_2 = rng.choice(genetic_alphabet, size = (n_random_sq, size_sq))

            # compute matchs
            matchs = many_exact_matching_with_nan_padding(sequences_1, sequences_2, 
                                                          n_to_match, distance_func)

            mutation(sequences_1, p_mut)
            mutation(sequences_2, p_mut)    

            matchs_bis = many_exact_matching_with_nan_padding(sequences_1, sequences_2, 
                                                              n_to_match, distance_func)
            # matchs = np.ones_like(matchs)
            # print(matchs.shape)
            # matchs[0] += 1
            # rng.shuffle(matchs)
            # print(matchs.sum())
            # --- For histogram of score values
            if False:
                if not np.isnan(matchs).all():
                    try:
                        kde = gaussian_kde(matchs[np.logical_not(np.isnan(matchs))].ravel())
                    except:
                        print(np.unique(matchs, return_counts = True))
                        raise
                    max_score = 200#2**(int(a)+1)*n_to_match
                    range_of_interest = np.linspace(-max_score, max_score, 100)
                    #np.min(scores)-3*kde.factor, np.max(scores)+3*kde.factor, 100)
                    print(kde.pdf(range_of_interest).sum()/(max_score/50))
                    ax.plot(range_of_interest, kde.pdf(range_of_interest), 
                            label = f't : {n_to_match}; M : {round(np.logical_not(np.isnan(matchs)).sum()/(n_random_sq**2), 2)}')
                else:
                    pass  # to next all necessary iterators
            # --- For breaking/building connections with mutations
            elif True:
                created = np.logical_and(np.isnan(matchs), np.logical_not(np.isnan(matchs_bis))).sum()
                destroyed = np.logical_and(np.logical_not(np.isnan(matchs)), np.isnan(matchs_bis)).sum()
                modified = (np.abs(matchs - matchs_bis) > 0).sum()
                initial = np.logical_not(np.isnan(matchs)).sum()
                result[i] = [created, destroyed, modified]
                result[i] /= initial
                # ax.scatter([0], [np.isnan(matchs).sum()], label = f't : {n_to_match}', marker = next(markers))


            # np.unique is sorted so result is (n_-1, n_0, n_+1)
            # values, result_temp = np.unique(matchs - matchs_bis, return_counts=True)
            # result[i, values] = result_temp/matchs.sum()   # normalizing with the amount of connections before mutation

        ax.plot(p_muts, result[:,0], ls = linestyle, label = f'Created connections')
        ax.plot(p_muts, result[:,1], ls = linestyle, label = f'Destroyed connections')
        ax.plot(p_muts, result[:,2], ls = linestyle, label = f'Modified connections')


        ax.set_title(f'''
        Mutation type : {mutation.__name__}''')
#    Alphabet size : {len(genetic_alphabet)}''')
    ax.legend()


plt.suptitle(f'''Number of sequences = {n_random_sq} --- Sequence Size = {size_sq}
{['Random Matching', 'Subsequence Matching'][int(matching_type == 'subsequence')]} --- Execution in {round(time() - t0, 1)}s''')
plt.show()
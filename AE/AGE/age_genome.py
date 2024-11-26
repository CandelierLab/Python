# genetic alphabet -> actual latin one '(26 characters seems to be enough)
# define device set
import string
import numpy as np
from functools import partial
from copy import deepcopy, copy
from time import time as time
from AE.AGE.string_alignement import score_alignement, rng    # check string_alignment for rng seeding (maybe create a separate file for it ?)
import matplotlib.pyplot as plt

from AE.AGE.string_alignement import score_alignement_with_history as score_alignement


from AE.Network import ANN as ann


genetic_alphabet = np.array(list(range(20)))
term_token = (19, 4, 17, 12)
parm_token = (15, 0, 17, 12)
neum_token = (13, 4,  0, 12)
neup_token = (13, 4,  0, 15)
stik_token = (18, 19, 8, 10)
tokens = {term_token : 'TERM', parm_token : 'PARM', neum_token : 'NEUM', neup_token : 'NEUP', stik_token : 'STIK'}
translate = lambda tk : tokens[tk]
genetic_alphabet_str = string.ascii_uppercase
numerical_value_reference = rng.choice(genetic_alphabet, size = 10)
# returns a character
random_letter = lambda : rng.choice(genetic_alphabet)
# returns an array of characters
random_sequence = lambda n : rng.choice(genetic_alphabet, size = n)

# Translate back a device from extracted to full sequence 

def reinsert_device(device_listform):
    return sum([(list(k))  for t in device_listform for k in t[::-1] if k is not None], [])

# A device has a genetic mapping (mostly)
        
# Device overlapping is supposed to be excluded (gene overlapping exists, but CM preliminary research has found it cumbersome (see p.66 thesis))

class device():
    def __init__(self, device_token, n_terms, n_parms, optional = None):   # if not None optional is the number [n_t, n_p] of additional terms/parms allowed; will be comapred to ints
        self.token = device_token
        self.terms = [[]]*n_terms
        self.parms = [[]]*n_parms
        if optional is None:
            self.requirement =  [n_terms, n_parms]
            self.max_optional = [n_terms, n_parms]
        else:  # for devices with a variable number of coding sections
            self.requirement =  [n_terms, n_parms]
            self.max_optional = [n_terms + optional[0], n_parms + optional[1]]
    def generate_sequence(self, term_token, parm_token, sq_gen):
        token_part= [*self.token,]
        term_part = [[*sq_gen(), *term_token] for i in range(len(self.terms))]
        parm_part = [[*sq_gen(), *parm_token] for i in range(len(self.parms))]
        # print(token_part)
        term_part = (sum(term_part, []))
        parm_part = (sum(parm_part, []))
        return token_part + term_part + parm_part
    
    def generate_tuples(self, term_token, parm_token, sq_gen):
        return ([(self.token,None)]
                     + [(term_token, sq_gen()) for i in range(len(self.terms))]
                     + [(parm_token, sq_gen()) for i in range(len(self.parms))])
    def evaluate_param(self, parm_sq, sqmin = 65, sqmax = 90*5, fmin = 0, fmax = 1, scaling = 'linear'):
        junk, x = score_alignement(parm_sq, numerical_value_reference)
        calc = (x -sqmin)/(sqmax-sqmin)
        if scaling == 'linear':
            return calc *(fmax-fmin) + fmin



# A list of devices which is able to return random new devices
class devices_generator():
    def __init__(self, devices_iterable, term_token = term_token, parm_token = parm_token):
        self.devices_collection = {d.token : d for d in devices_iterable}
        self.term_token = term_token
        self.parm_token = parm_token
        self.device_tokens = set([device.token for device in devices_iterable])

        self.ssg = partial(random_sequence, n = 5) #small_sequence_generator
    def generate(self, which = None):
        if which is None:
            return rng.choice(tuple(self.devices_collection.values())).generate_sequence(self.term_token, self.parm_token, self.ssg)
        return (self.devices_collection[which]).generate_sequence(self.term_token, self.parm_token, self.ssg)


# A genome knows its genetic code; it is able to mutate and extract a device list from its chromosomes

class genome():
    def __init__(self, g_alphabet = genetic_alphabet, token_size = 4, term_token = term_token, parm_token = parm_token,
                    devices_generator = None, device_interaction_map = None, # genetic code
                    chrom_min_init = 5, chrom_max_init = 15, chrom_number_init = 4):   # genome size

        self.ga = g_alphabet

        self.device_gen = devices_generator
        self.DIM = device_interaction_map 
        self.device_tokens = devices_generator.device_tokens
        self.term_sequence_max_size = 10
        self.tk_size = token_size
        self.token_collection = {term_token, parm_token} | self.device_tokens
        self.chromosomes = list([random_sequence(rng.integers(chrom_min_init, chrom_max_init))
                            for i in range(chrom_number_init)])
        self.update_len()

    # that one is going to be called a lot, so let's write it down properly
    def update(self):
        self.update_len()

    def update_len(self):
        self.chr_len = [len(chrom) for chrom in self.chromosomes]

    def __str__(self):
        return ','.join([str(np.array(chrom)) for chrom in self.chromosomes])

    def add_device_token(self, new_token):
            self.device_tokens |= set((new_token,)) 
            self.token_collection |= set((new_token,)) 

    # Returns the complementary to a sequence
    # aka the sequence silencing the interaction
    def complement_sequence(self, sq):
        half_alphabet_size = int(len(genetic_alphabet)/2)
        sq_comp = [self.ga[(char) - half_alphabet_size] for char in sq]
        return sq_comp

    # === Manage Mutations ================================================================================================

    # --- Single Nucleotide ------------------------------------------------------------
    # as noted in the thesis (p. 113 note 15), it is more efficient to roll for amount of mutations -> position of mutations rather than 'is there mutation' for each nucleotide

    def nuc_insert(self, p_mut_insert = .01): #p_mut_insert per nucleotide pair 
        
        # using np.array(chr_len) to use -1 on it
        
        to_insert = rng.binomial(np.array(self.chr_len)-1, p_mut_insert)
        places_to_insert = [rng.integers(1, self.chr_len[i] - 1, size = to_insert[i]) 
                            for i in range(len(self.chr_len))]
        
        for k in range(len(self.chromosomes)):
            if places_to_insert[k] is not None:
                for place in places_to_insert[k]:
                    self.chromosomes[k].insert(place, random_letter())
                    # new_nuc = random_letter()
                    # # print(self.chromosomes[k])
                    # self.chromosomes[k] = insert_string(self.chromosomes[k], place, new_nuc)
                    # places_to_insert[k][places_to_insert[k] > place] += 1
        self.update()

    def nuc_del(self, p_nd = .01):#p_mut_del per nucleotide 
        to_del = rng.binomial(self.chr_len, p_nd)
        
        places_to_del = [rng.choice(self.chr_len[i], size = to_del[i], replace = False) for i in range(len(self.chr_len))]

        # counter - sorting so del does not mess up the order
        places_to_del = [np.sort(p)[::-1] for p in places_to_del]


        for k in range(len(self.chromosomes)):
            if places_to_del[k] is not None:
                for place in places_to_del[k]:
                    try:
                        self.chromosomes[k].pop(place)
                    except IndexError:
                        print(self)
                        print(places_to_del)
                        print(len(self.chromosomes[k]))
                        print(place)

                        raise
                    # self.chromosomes[k] = f'{self.chromosomes[k][:place]}{self.chromosomes[k][place+1:]}'
                    # places_to_del[k][places_to_del[k] > place] += 1
        self.update()

    def nuc_sub(self, p_ns = .01):
        to_sub = rng.binomial(self.chr_len, p_ns)
        places_to_sub = [rng.integers(0, self.chr_len[i], size = to_sub[i]) for i in range(len(self.chr_len))]

        for k in range(len(self.chromosomes)):
            if places_to_sub[k] is not None:
                for place in places_to_sub[k]:
                    try:
                        self.chromosomes[k][place] = random_letter()
                    except TypeError:
                        print(list(self.chromosomes[k]))
                        print('')
                        print(len(self.chromosomes[k]))
                        print(place)

                        raise

        self.update()

    def single_nucleotide_mutate(self, p_mut = [.1]): #compilation of the three mutations above
        to_change = rng.binomial(np.array([self.chr_len]*3).T - np.array([1,0,0]), p_mut)
        # to make sure no one tries to access out of the list, order of operations will be substitute - insert - delete
        places_to_sub = [rng.integers(0, self.chr_len[i], size = to_change[i][1]) for i in range(len(self.chr_len))]
        places_to_del = [rng.integers(0, self.chr_len[i], size = to_change[i][2]) for i in range(len(self.chr_len))]
        places_to_ins = [rng.integers(1, self.chr_len[i] - 1, size = to_change[i][0]) 
                            for i in range(len(self.chr_len))]

        for k in range(len(self.chromosomes)):
            if (places_to_sub[k]) is not None:
                for place in places_to_sub[k]:
                    self.chromosomes[k].insert(place, random_letter())
            if (places_to_ins[k]) is not None:
                for place in places_to_ins[k]:
                    self.chromosomes[k].insert(place, random_letter())
                    places_to_ins[k][places_to_ins[k] > place] += 1
            if (places_to_del[k]) is not None:
                for place in places_to_del[k]:
                    self.chromosomes[k].pop(place)
        self.update()

    # --- Fragments mutations -----------------------------------------------------------------

    # for all fragment mutations, the random draw on whether or not it happens is assumed to be made previously
    def choose_fragments(self, n_frag, k_chrom = None):  # fragments can superpose

        # in this case attribution of nfrag to chroms is ambiguous
        assert (k_chrom is not None) or (len(n_frag) == len(self.chromosomes)), f'k_chrom = {k_chrom}, n_frag = {n_frag}, chroms = {self.chromosomes}'
        
        try:
            for i, k in enumerate(k_chrom):
                numbers = rng.integers(0, len(self.chromosomes[k]), 2*n_frag[i])
                fragments = np.array([numbers]).reshape((n_frag[i], 2))
                fragments.sort(axis = 1)
        except TypeError:   # k_chrom is not iterable
            if k_chrom is None:
                for i, n in enumerate(n_frag):
                    numbers = rng.integers(0, self.chr_len[i], 2*n)
                    fragments = np.array([numbers]).reshape((1, n, 2))
                    fragments.sort(axis = -1)
            else:
                try:
                    numbers = rng.integers(0, self.chr_len[k_chrom], 2*n_frag)
                    fragments = numbers.reshape((n_frag, 2))
                    fragments.sort(axis = 1)
                except IndexError: # k_chrom is not an int / n_frag is a list
                        fragments = np.array([numbers]).reshape((1, n, 2))
                        fragments.sort(axis = -1)
        return fragments

    def frag_dup(self, p_f2 = .01):
        whether_to_change = rng.choice([0, 1], p = [1-p_f2, p_f2], size = len(self.chromosomes)) #number of chr is low so we draw for each
        # choose slices from each chromosome
        fragments = self.choose_fragments(whether_to_change)
        # pick them up
        fragments_strings = ([self.chromosomes[k][start:end]  for k, chr_f in enumerate(fragments) for start, end in chr_f])
        # assign them to random locations on random chromosomes   (doing those draws separately)
        if len(self.chromosomes) == 1:
            chrom_to_go = np.zeros(len(fragments_strings), dtype = int)
        else:
            chrom_to_go = rng.integers(0, len(self.chromosomes) - 1, len(fragments_strings))
        # operations are considered as sequential and not simultaneous (if p_f2 is not too high there should be little to no overlap anyway)
        for i, new_frag in enumerate(fragments_strings):
            where_to_insert = rng.integers(1, self.chr_len[chrom_to_go[i]] - 1)
            self.chromosomes[chrom_to_go[i]][where_to_insert:where_to_insert] = list(new_frag)

        self.update()
    
    def frag_comp_dup(self, p_fc = .01):
        whether_to_change = rng.choice([0, 1],p = [1-p_fc, p_fc], size = len(self.chromosomes)) #number of chr is low so we draw for each
        # choose slices from each chromosome
        fragments = self.choose_fragments(whether_to_change)
        # pick them up
        fragments_strings = ([self.chromosomes[k][start:end]  for k, chr_f in enumerate(fragments) for start, end in chr_f])
        fragments_strings = ([self.chromosomes[k][start:end]  for k, chr_f in enumerate(fragments) for start, end in chr_f])
        # assign them to random locations on random chromosomes   (doing those draws separately)
        if len(self.chromosomes) == 1:
            chrom_to_go = np.zeros(len(fragments_strings), dtype = int)
        else:
            chrom_to_go = rng.integers(0, len(self.chromosomes) - 1, len(fragments_strings))
        # operations are considered as sequential and not simultaneous (if p_f2 is not too high there should be little to no overlap anyway)
        for i, new_frag in enumerate(fragments_strings):
            where_to_insert = rng.integers(1, self.chr_len[chrom_to_go[i]] - 1)
            self.chromosomes[chrom_to_go[i]][where_to_insert:where_to_insert] = list(self.complement_sequence(new_frag))

        self.update()

    def frag_transp(self, p_ft = .01):
        whether_to_change = rng.choice([0, 1],p = [1-p_ft, p_ft], size = len(self.chromosomes)) #number of chr is low so we draw for each
        # choose slices from each chromosome
        fragments = self.choose_fragments(whether_to_change)
        # pick them up
        fragments_strings = ([self.chromosomes[k][start:end]  for k, chr_f in enumerate(fragments) for start, end in chr_f])
        # assign them to random locations on random chromosomes   (doing those draws separately)
        if len(self.chromosomes) == 1:
            chrom_to_go = np.zeros(len(fragments_strings), dtype = int)
        else:
            chrom_to_go = rng.integers(0, len(self.chromosomes) - 1, len(fragments_strings))
        # deletion first, insertion second
        for k, frags in enumerate(fragments):
            for f in frags[::-1]:  # going through backwards so we don't modify list index 
                self.chromosomes[k][slice(*f)] = []

        for i, new_frag in enumerate(fragments_strings):
            where_to_insert = rng.integers(1, self.chr_len[chrom_to_go[i]] - 1)
            self.chromosomes[chrom_to_go[i]][where_to_insert:where_to_insert] = list(new_frag)

        self.update()

    def frag_del(self, p_fd = .01):
        whether_to_change = rng.choice([0, 1],p = [1-p_fd, p_fd], size = len(self.chromosomes)) #number of chr is low so we draw for each
        # choose slices from each chromosome
        fragments = self.choose_fragments(whether_to_change)
        for k, frags in enumerate(fragments):
            for f in frags[::-1]:  # going through backwards so we don't modify list index 
                self.chromosomes[k][slice(*f)] = []
        self.update()

    def mutate_device_insertion(self, p_di = .01):
        whether_to_change = rng.choice([0, 1],p = [1-p_di, p_di], size = len(self.chromosomes)) #number of chr is low so we draw for each
        for k in range(len(self.chr_len)):
            if whether_to_change[k]:
                new_device = self.device_gen.generate()
                
                try:
                    where_to_insert = rng.integers(1, len(self.chromosomes[k]) - 1)
                except ValueError:  # manage where_to_insert when len(chromosome) <= 2
                    if len(self.chromosomes[k]) == 2 or len(self.chromosomes[k]) == 1:
                        where_to_insert = 1
                    elif len(self.chromosomes[k]) == 0:
                        where_to_insert = 0
                    else:
                        print(len(self.chromosomes[k]))
                        raise
                self.chromosomes[k][where_to_insert:where_to_insert] = list(new_device)
        self.update()

    # --- Chromosome - level mutations -----------------------------------------------------------

    def chrom_dup(self, p_c2 = .001):
        whether_to_change = rng.choice([0, 1],p = [1-p_c2, p_c2], size = (len(self.chromosomes), 2))
        for k in range(len(self.chr_len)):
            if whether_to_change[k,0]:
                if whether_to_change[k,1]:  # appends
                    self.chromosomes[k][len(self.chromosomes[k]):] = deepcopy(self.chromosomes[k])
                else:    # creates new chrom
                    self.chromosomes.append(deepcopy(self.chromosomes[k]))
        self.update()
    def chrom_del(self, p_cd = .001):
        whether_to_change = rng.choice([0, 1],p = [1-p_cd, p_cd], size = len(self.chromosomes))
        for k in range(len(self.chr_len))[::-1]:
            if whether_to_change[k]:
                    self.chromosomes.pop(k)
    # has to be random rolled at the population level
    # TODO when local/global scoring is handled, as it heavly depends upon it
    def chrom_cross(self, other_genome, lm = 20):
        pass
        self.update()

    # --- Genome - level mutations  ----------------------------------------------------------

    def genome_dup(self, p_g2 = .001):
        if rng.random() < p_g2:
            append_if_false = rng.choice([0, 1], size = len(self.chr_len))
            if append_if_false.all():
                self.chromosomes[len(self.chromosomes):] = deepcopy(self.chromosomes)
            else:
                for k, aif in enumerate(append_if_false):
                    if aif:
                        self.chromosomes[k][len(self.chromosomes):] = deepcopy(self.chromosomes[k])
                    else:
                        self.chromosomes[k][len(self.chromosomes[k]):] = deepcopy(self.chromosomes[k])

        self.update()

    # Relies on genome decoding and device extraction
    # TODO when device extraction has been managed
    def genome_trim(self, p_gt = .001):
        pass

    def mutate(self, p_array = np.zeros(12, dtype = float) + .00001):
        self.update()
        mutate_funcs = [self.nuc_insert, self.nuc_del, self.nuc_sub, 
                        self.frag_dup ,self.frag_comp_dup, self.frag_transp, self.frag_del, 
                        self.mutate_device_insertion,
                        self.chrom_dup, self.chrom_del, self.chrom_cross, 
                        self.genome_dup, self.genome_trim]
        
        assert len(mutate_funcs) == len(p_array), f'{len(mutate_funcs)} != {len(p_array)}'

        for i, f in enumerate(mutate_funcs):
            f(p_array[i])



    def extract_devices(self, k_chr):
        c = tuple(self.chromosomes[k_chr])
        devices = []
        last_tk_end = 0+ self.tk_size
        in_device = False
        max_index_for_current_conding_sequence = len(c)
        # max_last_device_index = len(c)

        # in case chromosome is empty:
        current = None
        required = True

        


        for i in range(0, len(c)-self.tk_size+1):
            # we were extracting a device, but it is invalid (too long)
            if in_device and i > max_index_for_current_conding_sequence:
                in_device = False
                devices.pop(-1)
                # max_last_device_index = len(c)     # should not be necessary

            # we found a new device
            if tuple(c[i:i+self.tk_size]) in self.device_tokens:
                # it means that our last, unfinished device has to be considered invalid before starting the new one
                if in_device: 
                    # current device is invalid
                    devices.pop(-1)
                # but we found a new one

                # print(f'new device token @ {i}')
                devices.append([(c[i:i+self.tk_size], None)])
                in_device = True
                max_index_for_current_conding_sequence = i + self.term_sequence_max_size
                required = self.device_gen.devices_collection[c[i:i+self.tk_size]].requirement
                maximal = self.device_gen.devices_collection[c[i:i+self.tk_size]].max_optional
                current = [0,0]
                last_tk_end = i + self.tk_size


            # we found a term/parm token while building a device (as all tokens in token_collection are either term, parm or device)
            elif in_device and c[i:i+self.tk_size] in self.token_collection:

                # it is a term token
                if self.device_gen.term_token == c[i:i+self.tk_size]:
                    # print(f'end of term token @ {i}')
                    devices[-1].append((self.device_gen.term_token, c[last_tk_end:i]))
                    current[0] += 1
                    # we finished the current device
                    if current == required:
                        in_device = False
                    # the current device is ill-formed, thus invalid
                    elif current[0] > maximal[0]:
                        in_device = False
                        devices.pop(-1)
                    # the current device is unfinished, thus the next sequence is coding
                    else:
                        max_index_for_current_conding_sequence = i + self.term_sequence_max_size + self.tk_size

                # it is a parm token
                elif self.device_gen.parm_token == c[i:i+self.tk_size]:
                    # print(f'end of parm token @ {i}')
                    devices[-1].append((self.device_gen.parm_token, c[last_tk_end:i]))
                    current[1] += 1
                    # we finished the current device
                    if current == required:
                        in_device = False
                    # the current device is ill-formed, thus invalid
                    elif current[1] > maximal[1]:
                        in_device = False
                        devices.pop(-1)
                    # the current device is unfinished, thus the next sequence is coding
                    else:
                        max_index_for_current_conding_sequence = i + self.term_sequence_max_size + self.tk_size

                

                last_tk_end = i + self.tk_size
        # Last device found was invalid and not catched :
        # - there was at least one device found (current is not None)
        # - last device found was invalid (current != required)
        # - last device was not catched (not in_device)
        if current is not None and in_device and  current != required:
            devices.pop(-1)

        assert np.array([self.device_gen.devices_collection[d[0][0]].requirement 
                         == np.array([[t[0] == term_token, t[0] == parm_token] for t in d]
                                     ).sum(axis = 0) for d in devices]).all(), f'{devices}, {c}'
        
        

        return devices

    # def interact_devices(self, all_devs):
    #     # List all terminals and parameters
    #     device_type = []
    #     terminals = []
    #     terminal_ids = []
    #     parameters = []
    #     parameter_ids = []
    #     for i, device in enumerate(all_devs):
    #         device_type.append(device[0][0])
    #         j = 0
    #         k = 0
    #         for sq_type, small_sequence in device:
    #             if sq_type == self.device_gen.term_token:
    #                 terminals.append(small_sequence)
    #                 terminal_ids.append([i, j])
    #                 j += 1
    #             elif sq_type == self.device_gen.parm_token:
                    
    #                 parameters.append(self.device_gen.devices_collection[device[0][0]].evaluate_param(small_sequence))
    #                 parameter_ids.append([i,k])
    #                 k += 1

    #     # Determine interaction strength matrix
    #     t_interaction = np.array([[score_alignement(t1, t2)[1] for t2 in terminals] for t1 in terminals], dtype = float)
    #     t_interaction[np.diag_indices(t_interaction.shape[0])] *= 0
    #     network_base = (np.array(device_type), np.array(t_interaction), np.array(terminal_ids), parameters, parameter_ids)




    #     return network_base



neuron_exct_device = device(neup_token, 2, 0)
neuron_inhi_device = device(neum_token, 2, 0)
segment_device = device(stik_token, 2, 1)

acrobot_devices = devices_generator([neuron_exct_device, neuron_inhi_device, segment_device])



class acrobot_genome(genome):
    def __init__(self, segment_init = 2, sensor_init = 1, neuron_init = 'dense', **kwargs):
        super().__init__(devices_generator = acrobot_devices, 
                       chrom_min_init = 0, chrom_max_init = 0, chrom_number_init = 0,
                       **kwargs)
        try:
            segments = [self.device_gen.devices_collection[stik_token].generate_tuples(self.device_gen.term_token, 
                                                                                self.device_gen.parm_token, 
                                                                                self.device_gen.ssg) for i in range(segment_init)]
        except:
            print(locals())
            raise    
        self.pivot_sq = [0, 0, 0]   # discuss changes

        if neuron_init == 'dense':
            network = []
            network.append([(neup_token, None), (term_token, self.device_gen.ssg()), (term_token, self.device_gen.ssg())])
            # n_out = segment_init
            # n_in = sensor_init
            # for i in range(1, n_out):
            #     network.append([('NEUP', None), ('TERM', self.device_gen.ssg()), ('TERM', variate_sequence(segments[i][1][1]))])
            
            # for i in range(n_in):
            #     network.append([('NEUP', None), ('TERM', variate_sequence(segments[i][2][1])), ('TERM', self.device_gen.ssg())])

        segment_sequences = [reinsert_device(s) for s in segments]
        network_sequences = [reinsert_device(s) for s in network]

        to_be_inserted = segment_sequences + network_sequences
        rng.shuffle(to_be_inserted)

        thing = np.concatenate([np.concatenate((t,random_sequence(5))) for t in to_be_inserted])
        self.chromosomes = [list(np.concatenate((random_sequence(5), thing)))]


    # reference for f(score_alignement) = edge_weight
    # weights in [0; 1]
    # score is an array of floats
    def alignement_to_weight(self, score, lowclip = 5.0, highclip = 30.0, type = 'linear'):
        score[score <= lowclip] *= 0.0
        score[score >= highclip] = highclip
        if type == 'linear':
            return score/highclip
        else:
            raise NotImplementedError

    # the number of string matchings to do heavily depends on in/out sequences; thus suppressing genome.interact_devices seems as a decent idea

    def build_devices(self, all_devs):
        if len(all_devs) == 0:
            # nothing
            return np.array([[]]), []

        # start with building the body
        # reference string for anchor : self.pivot_sq 
        
        all_devs = np.array(all_devs, dtype = list)
        device_type = np.array([(dev[0][0]) for dev in all_devs])
        stik_mask = (device_type == stik_token).all(axis = 1)

    
        # checking body exists
        if stik_mask.sum() == 0:
            # no body -> no possibility to use a brain, so we return void instead of builiding it
            return np.array([[]]), []
        elif stik_mask.sum() == 1:
            # One segment = 0 degrees of freedom
            # -> no action
            # --> return void
            return np.array([[]]), []

        # print(t_useful_interactions)
        body = [[],]*stik_mask.sum()
        available_for_placement = list(range(stik_mask.sum()))
        # Building the body
        # - first segment
        score_with_pivot = [score_alignement(dev[1][1], self.pivot_sq)[1] for dev in all_devs[stik_mask]]
        try:
            body[0] = int(np.argmax(score_with_pivot))
        except:
            print(score_with_pivot)
            raise
        available_for_placement.pop(body[0])
        for k in range(len(body)-1):
            interactions_to_consider = [score_alignement(dev[1][1], all_devs[stik_mask][body[k]][2][1])[1] for dev in all_devs[stik_mask][available_for_placement]]
            #[t_interaction[i,body[k]] for i in available_for_placement]
            winning_term_arg = np.argmax(interactions_to_consider)
            body[k+1] = copy(available_for_placement[winning_term_arg])
            available_for_placement.pop(winning_term_arg)
       
       
        # network_ins/out = body
        devs_from_body_ordered = np.array(all_devs, dtype = object)[stik_mask][body]

        network_hidden_mask = np.logical_or((device_type == neup_token).all(axis = 1), (device_type == neum_token).all(axis = 1))
        





                    # Input - Hidden
        
        edges_in_hid = [[score_alignement(dev[1][1], Input[3][1])[1] for Input in devs_from_body_ordered] 
                     for dev in np.array(all_devs, dtype = object)[network_hidden_mask]]

                     # Input - Ouput
        edges_in_out = [[score_alignement(dev[1][1], Input[3][1])[1] for Input in devs_from_body_ordered] 
                     for dev in devs_from_body_ordered[:-1]]

                     # Hidden - Output
        edges_hid_out = [[score_alignement(Output[1][1], dev[2][1])[1] for dev in np.array(all_devs, dtype = object)[network_hidden_mask]] 
                     for Output in devs_from_body_ordered[:-1]]   # reorder as body and exclude last

                     # Hidden - Hidden
        edges_hid_hid = [[score_alignement(dev_1[1][1], dev_2[2][1])[1] for dev_2 in np.array(all_devs, dtype = object)[network_hidden_mask] ]
                       for dev_1 in np.array(all_devs, dtype = object)[network_hidden_mask]]
        


        # print(np.array(edges_in_hid).shape)
        # print(np.array(edges_in_out).shape)
        # print(np.array(edges_hid_hid).shape)
        # print(np.array(edges_hid_out).shape)

        e_in = edges_in_hid + edges_in_out
        e_hid = edges_hid_hid + edges_hid_out

        # print(np.array(e_in).shape)
        # print(np.array(e_hid).shape)
        try:
            net_adj_M = np.concatenate((e_in, e_hid), axis = 1)
        except:
            if e_in == []:
                if e_hid == []:
                    net_adj_M = np.array([[]])
                else:
                    net_adj_M = np.array(e_in)
            else:
                raise
    
        # print(np.array(net_adj_M))
        net_adj_M = self.alignement_to_weight(np.array(net_adj_M, dtype = float))    

        network_structure = (['IN']*len(devs_from_body_ordered) + [translate(dev_1[0][0]) 
                                                                   for dev_1 in all_devs 
                                                                   if dev_1[0][0] in {neup_token, neum_token}] + ['OUT']*(len(devs_from_body_ordered)-1))
        

        # === Debugging material ===

        # arr_struct = np.array(network_structure)

        # n_in = (arr_struct == 'IN').sum()
        # n_hid = np.logical_or(arr_struct == 'NEUP', arr_struct == 'NEUM').sum()
        # n_out = (arr_struct == 'OUT').sum()

        # assert n_out == n_in -1
        # print(n_in, n_hid, n_out)
        # assert net_adj_M.shape == (n_hid + n_out, n_in + n_hid), f'{net_adj_M} -- {edges_in_hid} - {edges_in_out} - {edges_hid_hid} - {edges_hid_out}'

        return net_adj_M, network_structure


def add_edges(net, adjacency, n_in, n_out = 0):
    for i, adj_line in enumerate(adjacency):
        for j, weigth in enumerate(adj_line):
            if weigth > 0:
                net.add_edge(i, j + n_in, weigth)

    return net

def fitness(net_AM, net_struct):

    result = 0
    # 1 - I want about 10 segments and 5 neurons
    nseg = sum([typ == 'IN' for typ in net_struct])
    nneu = sum([typ[:2] == 'NEU' for typ in net_struct])
    result -= (10-nseg)**2
    result -= (5-nneu)**2

    # 2 - I want few, high-value edges
    if net_AM.shape != (1,0):
        maxedge = np.max(net_AM)
        nhigh = (net_AM > maxedge*.9).sum()
        result += (maxedge * 10)**2
        result -= (5 - nhigh) ** 2
    
    nedg = (net_AM>0).sum()
    result -= nedg



    return result



def build_net(adjacency, structure):
    net = ann.ANN(default_activation='tanh')
    n_in = 0
    for node in structure:
        if node == 'NEUM':
            act = lambda x : -x
        elif node == 'IN':
            n_in += 1
            act = None
        else:
            act = None
        net.add_node(1, node == 'IN', node == 'OUT', 0, act)
    
    return add_edges(net, adjacency.T , n_in)


standard_mutate_rate = np.array([.001, .001, .001, 
                                .01, .0, .01, .01, 
                                .01,
                                .001, .001, .1,
                                .001, .01,
                                ])


if __name__ == "__main__":

    print('----------------------------')
            # mutate_funcs = [self.nuc_insert, self.nuc_del, self.nuc_sub, 
            #                 self.frag_dup ,self.frag_comp_dup, self.frag_transp, self.frag_del, 
            #                 self.chrom_dup, self.chrom_del, self.chrom_cross, 
            #                 self.genome_dup, self.genome_trim]
    standard_mutate_rate = np.array([.001, .001, .001, 
                                    .01, .0, .01, .01, 
                                    .01,
                                    .001, .001, .1,
                                    .001, .01,
                                    ])
    # def fitness(net_AM, net_struct):
    #     return len(net_struct)


    n_gens = 1000
    n_pop = 100
    pop = [acrobot_genome() for n in range(n_pop)]
    pop = np.array(pop, dtype = object)
    t_last_gen = time()
    time_per_generation = np.zeros(n_gens)
    total_genome_length_per_generation = np.zeros(n_gens)
    for generation in range(n_gens):
        t_gen = time() - t_last_gen
        t_last_gen = time()
        time_per_generation[generation] = t_gen + .0
        print(f'--- {generation} --- {round(t_gen, 4)}s')
        for i, g in enumerate(pop):

            net_foundations = g.build_devices(sum([g.extract_devices(k) for k in range(len(g.chromosomes))], start = []))
            # g.fitness = sum([len(chrom) for chrom in g.chromosomes])
    
            g.fitness = fitness(*net_foundations)
        sorter = np.argsort([g.fitness for g in pop])
        pop = np.array(pop, dtype = object)[sorter]
        pop[:-1] = [deepcopy(pop[-1])  for k in range(len(pop)-1)]
        for n in range(len(pop)-1):
            try:
                pop[n].mutate(standard_mutate_rate)
            except:
                print([np.array(j) for j in (pop[n].chromosomes)])
                raise
        
        total_genome_length_per_generation[generation] = (sum([sum([len(g.chromosomes[k]) for k in range(len(g.chromosomes))]) for g in pop]))
        print(total_genome_length_per_generation[generation]/len(pop))
        print(sum([g.fitness for g in pop])/len(pop), max([g.fitness for g in pop]))
        # total_number_of_devices_per_generation = (sum([sum([len(g.extract_devices(k)) for k in range(len(g.chromosomes))]) for g in pop]))

    print('----------------------------')
    g = pop[-1]
    all_devs  = g.extract_devices(0)
    anything = g.build_devices(all_devs)

    net = ann.ANN(default_activation='tanh')
    for node in anything[1]:
        if node == 'NEUM':
            act = lambda x : -x
        else:
            act = None
        net.add_node(1, node == 'IN', node == 'OUT', 0, act)
    add_edges(net, anything[0].T , 5)
    # print([[(i, j + 3) for j
            #  in range(anything[0].shape[1])] for i in  range(anything[0].shape[1])])
    print(net)
    # net.show()

    print('----------------------------')


    plt.scatter(total_genome_length_per_generation[1:] / n_pop, time_per_generation[1:], marker = 'o', c = range(1, n_gens))
    plt.yscale('log')
    plt.xscale('log')
    plt.title(f'{n_gens} generations, {n_pop} indivs, objective : realistically sized genome, alignment without history')
    plt.xlabel('Average genome size per individual')
    plt.ylabel('Calculation time (s)')
    plt.tight_layout()
    plt.show()
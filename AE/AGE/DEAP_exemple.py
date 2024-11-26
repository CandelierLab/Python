import deap as dp
import project
from deap import creator, base, tools

from AE.AGE.age_genome import acrobot_genome, build_net, standard_mutate_rate


from AE.AGE.age_genome import fitness as fit_realistic_devices
from copy import deepcopy, copy
from matplotlib import pyplot as plt
import random
import numpy as np
import time
random.seed(0)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", acrobot_genome, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Individuals have no attribute
# toolbox.register("individual", , creator.Individual)

toolbox.register("population", tools.initRepeat, list, creator.Individual)




# def evalAcrobotAGE(indiv):
#     net_AM, net_struct = indiv.build_devices(sum([indiv.extract_devices(k) for k in range(len(indiv.chromosomes))], start = []))
#     net = build_net(net_AM, net_struct)

#     # TODO : evaluate_simulation(net)
#     return [fit_realistic_devices(net_AM, net_struct)]


# toolbox.register("evaluate", evalAcrobotAGE)


def mutate_age_genome(g, m_rates = standard_mutate_rate):
    g.mutate(m_rates)


toolbox.register("mutate", mutate_age_genome)


# here we choose the selection algorithm !
toolbox.register("select", tools.selTournament, tournsize=3)


def evolve(n_pop = 100, n_gens = 200, max_fitness = 70, verbose = False):    # evolution stops if this fitness is reached



    pop = toolbox.population(n=n_pop)

    # Initialize time before first fitness computation
    tref = time.time()

    # Initialize fitness
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    fits = [ind.fitness.values[0] for ind in pop]
    all_fits = [copy(fits)] + n_gens * [[]]
    generation = 0

    # Begin the evolution
    while max(fits) < max_fitness and generation < n_gens:
        # A new generation
        generation = generation + 1
        if verbose :
            print(f"-- Generation %i -- {time.time() - tref}" % generation)
            tref = time.time()

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if verbose :
            print("  Evaluated %i individuals" % len(invalid_ind))

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        # Stock some for recap
        all_fits[generation] = copy(fits)

        if verbose :
            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)

    print("-- End of (successful) evolution --")

    np_all_fits = np.array(all_fits[:generation])

    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))


    plt.scatter(np.ravel([range(generation)] * n_pop), np.ravel(np_all_fits.T), marker = '+')
    plt.plot(range(generation), np.max(np_all_fits, axis = 1))

    plt.ylabel('Fitness')
    plt.xlabel('Generation')
    plt.show()

    return best_ind, np_all_fits
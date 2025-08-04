# genetic_algorithm/ga_core.py

import random
from ..config import (
    MIN_PHASE_DURATION, MAX_PHASE_DURATION, MUTATION_RATE, TOURNAMENT_SIZE
)

def create_chromosome(traffic_light_info):
    """
    Creates a random chromosome based on the number of green phases.
    """
    chromosome = []
    for tls_id in traffic_light_info:
        num_green_phases = len(traffic_light_info[tls_id]['green_phases'])
        for _ in range(num_green_phases):
            chromosome.append(random.randint(MIN_PHASE_DURATION, MAX_PHASE_DURATION))
    return chromosome

def selection(population_with_fitness):
    """
    Performs tournament selection to choose a parent chromosome.
    """
    tournament = random.sample(population_with_fitness, min(TOURNAMENT_SIZE, len(population_with_fitness)))
    tournament.sort(key=lambda x: x[1])
    return tournament[0][0]

def crossover(parent1, parent2):
    """
    Performs two-point crossover between two parent chromosomes.
    """
    if len(parent1) < 3:
        if len(parent1) == 0: return []
        if len(parent1) == 1: return [parent1[0]]
        crossover_point = random.randint(1, len(parent1) - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]

    point1 = random.randint(1, len(parent1) - 2)
    point2 = random.randint(point1 + 1, len(parent1) - 1)

    child = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
    return child

def mutate(chromosome):
    """
    Mutates a chromosome by randomly changing gene values.
    """
    mutated_chromosome = []
    for gene in chromosome:
        if random.random() < MUTATION_RATE:
            mutated_chromosome.append(random.randint(MIN_PHASE_DURATION, MAX_PHASE_DURATION))
        else:
            mutated_chromosome.append(gene)
    return mutated_chromosome

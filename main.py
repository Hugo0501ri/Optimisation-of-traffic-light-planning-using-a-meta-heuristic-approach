# main.py

import os
import matplotlib.pyplot as plt
from sumo_simulation.sumo_config_gen import (
    generate_network, generate_trips_and_routes, create_type_file, create_sumocfg
)
from sumo_simulation.sumo_runner import get_traffic_light_info, evaluate_fitness
from genetic_algorithm.ga_core import create_chromosome, selection, crossover, mutate
from genetic_algorithm.ga_utilities import load_chromosome, save_chromosome
from config import (
    NET_FILE, ROUTE_FILE, POPULATION_SIZE, NUM_GENERATIONS,
    BEST_CHROMOSOME_FILE
)

def run_genetic_algorithm(initial_chromosome=None):
    """
    Executes the genetic algorithm for traffic light optimization.
    """
    print("\n--- Preparing Simulation Environment ---")

    if not os.path.exists(NET_FILE) or not os.path.exists(ROUTE_FILE):
        print(f"INFO: Scenario files not found. Generating a NEW traffic scenario...")
        generate_network()
        generate_trips_and_routes()
    else:
        print(f"INFO: Using EXISTING traffic scenario (.net.xml and .rou.xml files).")

    create_type_file()
    create_sumocfg()
    print("INFO: Configuration files (.sumocfg, .type.xml) ready.")

    print("\n--- Analyzing Traffic Light Structure ---")
    traffic_light_info = get_traffic_light_info()
    if not traffic_light_info:
        print("WARNING – No traffic lights found. Optimization is pointless.")
        return

    num_genes = sum(len(info['green_phases']) for info in traffic_light_info.values())
    print(f"INFO: {len(traffic_light_info)} traffic lights found, requiring a chromosome of {num_genes} genes.")

    print("\n--- Initializing Population ---")
    population = []
    is_initial_valid = (initial_chromosome is not None and
                        isinstance(initial_chromosome, list) and
                        len(initial_chromosome) == num_genes and
                        all(isinstance(x, int) for x in initial_chromosome))

    if is_initial_valid:
        print("INFO: Valid initial chromosome provided and will be injected into the population.")
        population.append(initial_chromosome)
        for _ in range(POPULATION_SIZE - 1):
            population.append(create_chromosome(traffic_light_info))
    else:
        if initial_chromosome is not None:
             print(f"WARNING: Provided initial chromosome is invalid.")
        print("INFO: Creating a fully random initial population.")
        for _ in range(POPULATION_SIZE):
            population.append(create_chromosome(traffic_light_info))

    best_fitness_history = []
    average_fitness_history = []
    best_overall_fitness = float('inf')
    best_overall_chromosome = []

    for gen in range(NUM_GENERATIONS):
        print(f"\n--- Generation {gen + 1}/{NUM_GENERATIONS} ---")

        population_with_fitness = []
        for i, chrom in enumerate(population):
            print(f"  Evaluating individual {i+1}/{POPULATION_SIZE}...", end=' ', flush=True)
            fitness = evaluate_fitness(chrom, traffic_light_info)
            population_with_fitness.append((chrom, fitness))
            print(f"Fitness = {fitness:.2f}")

        population_with_fitness.sort(key=lambda x: x[1])
        best_gen_chromosome, best_gen_fitness = population_with_fitness[0]

        current_fitnesses = [f for _, f in population_with_fitness]
        avg_gen_fitness = sum(current_fitnesses) / len(current_fitnesses)

        best_fitness_history.append(best_gen_fitness)
        average_fitness_history.append(avg_gen_fitness)

        if best_gen_fitness < best_overall_fitness:
            best_overall_fitness = best_gen_fitness
            best_overall_chromosome = best_gen_chromosome

        print(f"Best fitness of generation: {best_gen_fitness:.2f} | Average fitness: {avg_gen_fitness:.2f}")

        new_population = [best_gen_chromosome]
        while len(new_population) < POPULATION_SIZE:
            parent1 = selection(population_with_fitness)
            parent2 = selection(population_with_fitness)
            child = crossover(parent1, parent2)
            mutated_child = mutate(child)
            new_population.append(mutated_child)

        population = new_population

    print("\n--- Optimization Complete! ---")
    print(f"Best overall fitness found: {best_overall_fitness:.2f}")
    print(f"Best chromosome (durations in s): {best_overall_chromosome}")

    if best_overall_chromosome:
        save_chromosome(best_overall_chromosome)

    print("\n--- Convergence History ---")
    for i, (best_f, avg_f) in enumerate(zip(best_fitness_history, average_fitness_history)):
        print(f"Generation {i+1}: Best Fitness = {best_f:.2f}, Average Fitness = {avg_f:.2f}")

    try:
        plt.figure(figsize=(12, 7))
        plt.plot(range(1, NUM_GENERATIONS + 1), best_fitness_history, 'o-', label='Best fitness per generation')
        plt.plot(range(1, NUM_GENERATIONS + 1), average_fitness_history, 's--', label='Mean fitness per generation')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.title('Convergence of GA')
        plt.legend()
        plt.grid(True)
        plt.xticks(range(1, NUM_GENERATIONS + 1))
        convergence_plot_file = 'convergence_plot.png'
        plt.savefig(convergence_plot_file)
        print(f"\nINFO: Convergence plot saved to '{convergence_plot_file}'.")
    except Exception as e:
        print(f"WARNING: Error while creating the plot: {e}")

if __name__ == "__main__":
    print("=========================================================")
    print("    Starting Traffic Light Optimizer with GA & SUMO      ")
    print("=========================================================")

    print(f"\n>>> Step 1: Attempting to load best chromosome from '{BEST_CHROMOSOME_FILE}'...")
    loaded_chromosome = load_chromosome()

    if loaded_chromosome:
        print("\n>>> Step 2: Launching Genetic Algorithm.")
        print("INFO: A previous chromosome was loaded and will be used as a starting point.")
        run_genetic_algorithm(initial_chromosome=loaded_chromosome)
    else:
        print("\n>>> Step 2: Launching Genetic Algorithm.")
        print("INFO: No valid chromosome found. Starting with a fully random population.")
        run_genetic_algorithm(initial_chromosome=None)

    print("\n" + "="*70)
    print("Program finished.")
    print(f"The best result from this session has been appended to '{BEST_CHROMOSOME_FILE}'.")
    print("To continue optimization on the same scenario, simply re-run the script.")
    print("To start a new optimization on a new scenario, delete the .net.xml and .rou.xml files in SUMO_config.")
    print("="*70 + "\n")

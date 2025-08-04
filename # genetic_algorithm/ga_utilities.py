# genetic_algorithm/ga_utilities.py

import os
from ..config import SIMULATION_DURATION, VEHICLE_COUNT, BEST_CHROMOSOME_FILE

def save_chromosome(chromosome, filename=BEST_CHROMOSOME_FILE):
    """
    Saves a chromosome by appending it to a text file.
    """
    try:
        chromosome_str = ", ".join(map(str, chromosome))
        with open(filename, 'a') as f:
            f.write(chromosome_str + "\n")
        print(f"INFO – Best chromosome saved and appended to '{filename}'.")
    except IOError as e:
        print(f"WARNING: Could not append chromosome to '{filename}'. Error: {e}")

def load_chromosome(filename=BEST_CHROMOSOME_FILE):
    """
    Loads the last saved chromosome from a text file.
    """
    if not os.path.exists(filename):
        print(f"INFO: Save file '{filename}' does not exist yet.")
        return None

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        last_line = ""
        for line in reversed(lines):
            stripped_line = line.strip()
            if stripped_line:
                last_line = stripped_line
                break

        if not last_line:
            print(f"WARNING: File '{filename}' is empty or contains only empty lines.")
            return None

        chromosome_str_list = last_line.split(',')
        chromosome = []
        for s in chromosome_str_list:
            if s.strip():
                try:
                    chromosome.append(int(s.strip()))
                except ValueError:
                    print(f"WARNING: Non-numeric value ('{s.strip()}') found in '{filename}'.")
                    return None

        if not chromosome:
            print(f"WARNING: The last line of '{filename}' is malformed.")
            return None

        print(f"INFO – Last valid chromosome loaded from '{filename}'.")
        return chromosome

    except IOError as e:
        print(f"WARNING: Could not read file '{filename}'. Error: {e}")
        return None

def calculate_fitness(durations, waiting_times):
    """
    Calculates the fitness of a solution. A lower fitness value is better.
    """
    num_arrived = len(durations)
    num_uncompleted = VEHICLE_COUNT - num_arrived

    uncompleted_duration_contribution = num_uncompleted * SIMULATION_DURATION
    uncompleted_waiting_contribution = num_uncompleted * SIMULATION_DURATION

    total_duration = sum(durations) + uncompleted_duration_contribution
    total_waiting = sum(waiting_times) + uncompleted_waiting_contribution

    mean_duration = total_duration / VEHICLE_COUNT if VEHICLE_COUNT > 0 else (SIMULATION_DURATION * 2)
    mean_waiting = total_waiting / VEHICLE_COUNT if VEHICLE_COUNT > 0 else (SIMULATION_DURATION * 2)

    w1_duration, w2_waiting = 1.0, 0.5
    fitness = (w1_duration * mean_duration) + (w2_waiting * mean_waiting)

    return fitness

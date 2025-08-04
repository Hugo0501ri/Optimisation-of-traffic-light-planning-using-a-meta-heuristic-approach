# config.py

import os
import sys
import logging

# === Paths and General Configuration ===
SUMO_CONFIG_DIR = "SUMO_config"
OSM_FILE = os.path.join(SUMO_CONFIG_DIR, "map7_josm.osm")
NET_FILE = os.path.join(SUMO_CONFIG_DIR, "map7.net.xml")
TRIP_FILE = os.path.join(SUMO_CONFIG_DIR, "trips7.trips.xml")
ROUTE_FILE = os.path.join(SUMO_CONFIG_DIR, "routes7.rou.xml")
SUMOCFG_FILE = os.path.join(SUMO_CONFIG_DIR, "simulation7.sumocfg")
TYPE_FILE = os.path.join(SUMO_CONFIG_DIR, "types7.type.xml")
BEST_CHROMOSOME_FILE = "best_chromosome.txt"

# === Simulation Parameters ===
VEHICLE_COUNT = 250
SIMULATION_DURATION = 1000
STEP_LENGTH = 0.1
SIM_STEPS = int(SIMULATION_DURATION / STEP_LENGTH)

# === Environment Variables and SUMO Binaries ===
if 'SUMO_HOME' not in os.environ:
    print("CRITICAL – SUMO_HOME environment variable is not defined. Exiting script.")
    sys.exit(1)

SUMO_BINARY = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo')
NETCONVERT = os.path.join(os.environ['SUMO_HOME'], 'bin', 'netconvert')
DUAROUTER = os.path.join(os.environ['SUMO_HOME'], 'bin', 'duarouter')

# === Genetic Algorithm Parameters ===
POPULATION_SIZE = 20
NUM_GENERATIONS = 5
MUTATION_RATE = 0.2
TOURNAMENT_SIZE = 2
MIN_PHASE_DURATION = 5
MAX_PHASE_DURATION = 60

# --- Log Configuration ---
log = logging.getLogger()
log.setLevel(logging.CRITICAL)
if log.hasHandlers():
    log.handlers.clear()

os.makedirs(SUMO_CONFIG_DIR, exist_ok=True)

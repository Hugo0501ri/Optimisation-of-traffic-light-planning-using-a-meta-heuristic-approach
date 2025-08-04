# Traffic Light Optimization with Genetic Algorithm and SUMO

This project applies a **Genetic Algorithm (GA)** to optimize **traffic light durations** within a simulated urban network using **SUMO (Simulation of Urban Mobility)**. The goal is to reduce total trip durations and waiting times by evolving better traffic light timing strategies.

##  Key Features

- Dynamic generation of SUMO network and routes from an OpenStreetMap (.osm) file.
- Automatic detection and control of traffic lights via TraCI.
- Multi-generation Genetic Algorithm:
  - Tournament selection
  - Two-point crossover
  - Mutation with configurable rate
- Fitness function balancing trip duration and waiting time.
- Persistent storage of best solutions for future reuse.
- Convergence plot generation for visual analysis.

##  Project Files Overview

The project consists of several essential and generated files used throughout the optimization and simulation process:

###  Configuration and Input Files

- **map.osm**  
  OpenStreetMap file representing the road network used for simulation.  
  > You can edit this file using [JOSM](https://josm.openstreetmap.de/), a graphical OSM editor — but this is optional. Any valid `.osm` file can be used without modification.

- **simulation.sumocfg**  
  Main configuration file for running the SUMO simulation, referencing all required input files.

- **types.type.xml**  
  Definitions of vehicle types used in the simulation (e.g., speed, acceleration, length).

- **trips.trips.xml**  
  Generated file defining vehicle trips (departure and arrival points).

- **routes.rou.xml**  
  Contains detailed routes generated from the trips file.

- **map.net.xml**  
  SUMO network file generated from the `.osm` map using `netconvert`.

---

###  Genetic Algorithm Files

- **your_script.py**  
  Main Python script running the genetic algorithm and controlling SUMO via TraCI.

- **best_chromosome.txt**  
  Stores the best-performing chromosome (optimized traffic light durations) found during execution. If present, it's reused to initialize future runs.

- **convergence_plot.png**

## Genetic Algorithm Parameters

The genetic algorithm parameters can be adjusted directly in the script to control the optimization process:

| Parameter             | Description                                                   | Default |
|-----------------------|---------------------------------------------------------------|---------|
| `POPULATION_SIZE`     | Number of individuals per generation                          | 20      |
| `NUM_GENERATIONS`     | Total number of generations to run                            | 5       |
| `MUTATION_RATE`       | Probability of mutation per gene                              | 0.2     |
| `TOURNAMENT_SIZE`     | Number of chromosomes in tournament selection                 | 2       |
| `MIN_PHASE_DURATION`  | Minimum green light phase duration (seconds)                 | 5       |
| `MAX_PHASE_DURATION`  | Maximum green light phase duration (seconds)                 | 60      |
## Installation commands

Make sure you have **SUMO** installed and `SUMO_HOME` environment variable set:  
[SUMO installation instructions](https://sumo.dlr.de/docs/Installing.html)

Then install Python dependencies with:

```bash
pip install numpy pandas matplotlib
```
##  Running the Project

To start the optimization and simulation, run the main Python script:

```bash
python your_script.py
```
If the required .net.xml or .rou.xml files do not exist, the script will generate them automatically.

If a best_chromosome.txt file exists, it will be loaded to continue optimization from the previous best solution.

Otherwise, the genetic algorithm will start with a new random population.

  Fitness convergence plot automatically generated after execution.


---



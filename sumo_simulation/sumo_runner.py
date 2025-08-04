# sumo_simulation/sumo_runner.py

import os
import sys
import random
import traci
from ..config import (
    SUMO_BINARY, SUMOCFG_FILE, STEP_LENGTH, SIM_STEPS, MIN_PHASE_DURATION, MAX_PHASE_DURATION, SUMO_CONFIG_DIR
)
from ..genetic_algorithm.ga_utilities import calculate_fitness

def get_traffic_light_info():
    """
    Launches a short SUMO simulation to retrieve traffic light IDs and their green phase indices.
    """
    original_cwd = os.getcwd()
    os.chdir(SUMO_CONFIG_DIR)

    sumo_cmd = [SUMO_BINARY, "-c", os.path.basename(SUMOCFG_FILE), "--start", "--quit-on-end"]
    traci_port = 8813 + random.randint(0, 1000)

    try:
        traci.start(sumo_cmd, port=traci_port, label=f"init_tls_check_{traci_port}")
    except traci.exceptions.FatalTraCIError as e:
        print(f"CRITICAL – Could not start SUMO/TraCI for traffic light initialization. Error: {e}")
        os.chdir(original_cwd)
        sys.exit(1)

    traffic_lights = {}
    tls_ids = traci.trafficlight.getIDList()

    for tls_id in tls_ids:
        logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tls_id)[0]
        green_phases_indices = [i for i, phase in enumerate(logic.phases) if 'g' in phase.state.lower()]
        traffic_lights[tls_id] = {'green_phases': green_phases_indices, 'all_phases': logic.phases}

    traci.close()
    os.chdir(original_cwd)
    return traffic_lights

def evaluate_fitness(chromosome, traffic_light_info):
    """
    Runs a SUMO simulation with a given chromosome and returns the fitness.
    """
    original_cwd = os.getcwd()
    os.chdir(SUMO_CONFIG_DIR)

    sumo_cmd = [SUMO_BINARY, "-c", os.path.basename(SUMOCFG_FILE), "--start", "--quit-on-end",
                "--step-length", str(STEP_LENGTH), "--no-warnings",
                "--error-log", os.path.join(original_cwd, SUMO_CONFIG_DIR, "sumo_error.log")]

    traci_port = 8813 + random.randint(0, 1000)

    try:
        traci.start(sumo_cmd, port=traci_port, label=f"eval_{random.randint(1,10000)}")
    except traci.TraCIException as e:
        print(f"CRITICAL – Could not start SUMO/TraCI for evaluation. Error: {e}")
        os.chdir(original_cwd)
        return float('inf')

    gene_index = 0
    for tls_id, info in traffic_light_info.items():
        logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tls_id)[0]
        for phase_index in info['green_phases']:
            if gene_index < len(chromosome):
                duration = max(MIN_PHASE_DURATION, min(MAX_PHASE_DURATION, chromosome[gene_index]))
                logic.phases[phase_index].duration = duration
                gene_index += 1
            else:
                break
        traci.trafficlight.setCompleteRedYellowGreenDefinition(tls_id, logic)

    completed_trip_durations = []
    completed_trip_waiting_times = []
    active_vehicle_data = {}

    step = 0
    while step < SIM_STEPS:
        try:
            traci.simulationStep()
        except traci.TraCIException as e:
            print(f"WARNING: Error during simulation (step {step}). {e}")
            break

        sim_time = traci.simulation.getTime()

        for veh_id in traci.simulation.getDepartedIDList():
            active_vehicle_data[veh_id] = {'depart_time': sim_time, 'accumulated_waiting_time': 0}

        for veh_id in traci.vehicle.getIDList():
            if veh_id in active_vehicle_data:
                try:
                    active_vehicle_data[veh_id]['accumulated_waiting_time'] = traci.vehicle.getAccumulatedWaitingTime(veh_id)
                except traci.TraCIException:
                    pass

        for veh_id in traci.simulation.getArrivedIDList():
            if veh_id in active_vehicle_data:
                data = active_vehicle_data.pop(veh_id)
                duration = sim_time - data['depart_time']
                completed_trip_durations.append(duration)
                completed_trip_waiting_times.append(data['accumulated_waiting_time'])

        if traci.simulation.getMinExpectedNumber() == 0 and not traci.vehicle.getIDList():
             break

        step += 1

    traci.close()
    os.chdir(original_cwd)
    
    return calculate_fitness(completed_trip_durations, completed_trip_waiting_times)

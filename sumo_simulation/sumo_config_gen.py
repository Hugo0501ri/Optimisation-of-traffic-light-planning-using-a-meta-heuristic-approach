# sumo_simulation/sumo_config_gen.py

import os
import subprocess
import sys
import random
from xml.etree.ElementTree import Element, SubElement, ElementTree
from sumolib import net
from ..config import (
    NETCONVERT, DUAROUTER, OSM_FILE, NET_FILE, TRIP_FILE, ROUTE_FILE,
    TYPE_FILE, SUMOCFG_FILE, SUMO_CONFIG_DIR, VEHICLE_COUNT, SIMULATION_DURATION
)

def generate_network():
    """Generates the SUMO network file from the OSM file."""
    if not os.path.exists(OSM_FILE):
        print(f"CRITICAL – OSM file '{os.path.basename(OSM_FILE)}' not found.")
        sys.exit(1)

    print(f"INFO – Generating network from {os.path.basename(OSM_FILE)}...")
    try:
        command = [
            NETCONVERT, "--osm-files", os.path.basename(OSM_FILE),
            "-o", os.path.basename(NET_FILE), "--tls.discard-loaded", "false",
            "--tls.guess", "--tls.default-type", "static",
            "--junctions.join", "false", "--tls.guess.threshold", "2"
        ]
        subprocess.run(command, check=True, capture_output=True, text=True, cwd=SUMO_CONFIG_DIR)
        print(f"INFO – Network '{os.path.basename(NET_FILE)}' generated.")
    except subprocess.CalledProcessError as e:
        print(f"CRITICAL – netconvert error: {e.stderr}")
        sys.exit(1)

def get_border_edges(net_file):
    """Retrieves the incoming (entry) and outgoing (exit) edges of the network."""
    try:
        net_data = net.readNet(net_file)
        inputs = [e.getID() for e in net_data.getEdges() if not e.getIncoming()]
        outputs = [e.getID() for e in net_data.getEdges() if not e.getOutgoing()]
        return inputs, outputs
    except Exception as e:
        print(f"CRITICAL – Error reading network file '{net_file}': {e}")
        sys.exit(1)

def generate_trips_and_routes():
    """Generates random trip definitions and computes routes."""
    inputs, outputs = get_border_edges(NET_FILE)
    if not inputs or not outputs:
        print("CRITICAL – No entry/exit edges found in the network.")
        sys.exit(1)

    root = Element("routes")
    interval = SIMULATION_DURATION / VEHICLE_COUNT if VEHICLE_COUNT > 0 else 0
    for i in range(VEHICLE_COUNT):
        from_edge, to_edge = random.choice(inputs), random.choice(outputs)
        while to_edge == from_edge and len(outputs) > 1:
            to_edge = random.choice(outputs)

        depart_time = min(SIMULATION_DURATION, i * interval)
        SubElement(root, "trip", {"id": f"trip_{i}", "from": from_edge, "to": to_edge, "depart": f"{depart_time:.2f}"})

    ElementTree(root).write(TRIP_FILE, encoding="utf-8", xml_declaration=True)
    print(f"INFO – Trip file '{os.path.basename(TRIP_FILE)}' generated.")

    try:
        subprocess.run(
            [DUAROUTER, "--net-file", os.path.basename(NET_FILE), "-t", os.path.basename(TRIP_FILE), "-o", os.path.basename(ROUTE_FILE)],
            check=True, capture_output=True, text=True, cwd=SUMO_CONFIG_DIR
        )
        print(f"INFO – Route file '{os.path.basename(ROUTE_FILE)}' generated.")
    except subprocess.CalledProcessError as e:
        print(f"CRITICAL – duarouter error: {e.stderr}")
        sys.exit(1)

def create_type_file():
    """Creates a basic vehicle types file."""
    with open(TYPE_FILE, "w") as f:
        f.write('<routes><vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" maxSpeed="30"/></routes>')

def create_sumocfg():
    """Creates the main SUMO configuration file (.sumocfg)."""
    with open(SUMOCFG_FILE, "w") as fd:
        fd.write(f'<configuration><input><net-file value="{os.path.basename(NET_FILE)}"/><route-files value="{os.path.basename(ROUTE_FILE)}"/><additional-files value="{os.path.basename(TYPE_FILE)}"/></input><time><begin value="0"/><end value="{SIMULATION_DURATION}"/></time></configuration>')

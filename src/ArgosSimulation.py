import time
import re
from subprocess import Popen, PIPE
import os
from lxml import etree


def callArgosSimulation(argos_simulation_file, arena_radius, num_robots, sim_time, sim_id):
    parser = etree.XMLParser(remove_comments = False)
    etree.set_default_parser(parser)
    tree = etree.parse(argos_simulation_file)
    root = tree.getroot()
    for experiment in root.iter('experiment'):
        experiment.set("length", "%d" % sim_time)
    for loop_functions in root.iter('loop_functions'):
        loop_functions.set("num_robots", "%d" % num_robots)
        loop_functions.set("id_simulation", "%s" % sim_id)
        loop_functions.set("arena_radius", "%.3f" % arena_radius)
    tree.write(argos_simulation_file, xml_declaration = True)
    while True:
        try:
            process = Popen(["argos3", "-c", argos_simulation_file], stdout=PIPE, stderr=PIPE)
            break
        except Exception as e:
            print("Couldnt call argos simulation!\n" + str(e))
            time.sleep(1)

    return process

def checkProcessStatus(simulation, num_robots):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    process_has_end = False
    sim_results = dict()
    if simulation.simulationHasEnd():
        try:
            output, error = simulation.process.communicate()
            if simulation.process.returncode != 0: 
                raise Exception("Simulation %d failed! Process Error: %s" % (simulation.process.pid, error))

            out_decoded_raw = output.decode('utf-8', errors='ignore')
            out_decoded = ansi_escape.sub('', out_decoded_raw)
            data_line = None
            for line in out_decoded.split('\n'):
                if "RESULTS:" in line:
                    data_line = line
                    break
            if data_line is None:
                raise Exception(f"Could not find the 'RESULTS: ' line in the simulation output.\nFull Output:\n---\n{out_decoded}\n---")
            
            results_str = data_line.replace("RESULTS: ", "").strip()
            lines = results_str.split(' ')
            if len(lines) == (4 + num_robots):
                sim_results['disc'] = int(lines[0])
                sim_results['inf'] = int(lines[1])
                sim_results['frac disc'] = float(lines[2])
                sim_results['frac inf'] = float(lines[3])
                sim_results['disc robots'] = []
                for line in lines[4:]:
                    sim_results['disc robots'].append(int(line))
                process_has_end = True
            else:
                raise Exception(f"The results line has {len(lines)} fields, but expected {(4 + num_robots)}.\nLine Found: '{data_line}'\nFull Output:\n---\n{out_decoded}\n---")
        except Exception as e:
            print("Code Exception: %s" % (str(e)))
            exit(1)

    return process_has_end, sim_results

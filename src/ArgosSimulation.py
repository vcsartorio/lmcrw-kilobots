import time
import re
from subprocess import Popen, PIPE
import os
from lxml import etree


def callArgosSimulation(argos_file, arena_radius, num_robots, sim_time, sim_id):
    # 1. Cria um nome de arquivo exclusivo para esta execução
    directory = os.path.dirname(argos_file)
    base_name = os.path.basename(argos_file).replace('.argos', '')
    temp_argos_file = os.path.join(directory, f"{base_name}_id:{sim_id}.argos")

    # 2. Carrega o TEMPLATE (arquivo original)
    parser = etree.XMLParser(remove_comments = False)
    etree.set_default_parser(parser)
    tree = etree.parse(argos_file)
    root = tree.getroot()

    # 3. Modifica os parâmetros
    for experiment in root.iter('experiment'):
        experiment.set("length", "%d" % sim_time)
    for loop_functions in root.iter('loop_functions'):
        loop_functions.set("num_robots", "%d" % num_robots)
        loop_functions.set("id_simulation", "%s" % sim_id)
        loop_functions.set("arena_radius", "%.3f" % arena_radius)

    # 4. Salva noem um novo arquivo
    tree.write(temp_argos_file, xml_declaration = True)

    # 5. Chama a simulação
    while True:
        try:
            process = Popen(["argos3", "-c", temp_argos_file], stdout=PIPE, stderr=PIPE)
            break
        except Exception as e:
            print("Couldnt call argos simulation!\n" + str(e))
            time.sleep(1)

    return process, temp_argos_file

def checkProcessStatus(simulation, num_robots):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    process_has_end = False
    sim_results = dict()
    error_message = None

    if simulation.simulationHasEnd():
        try:
            output, error = simulation.process.communicate()
            if simulation.process.returncode != 0: 
                error_message = f"Simulation {simulation.process.pid} failed! Process Error: {error}"
            else:
                out_decoded_raw = output.decode('utf-8', errors='ignore')
                out_decoded = ansi_escape.sub('', out_decoded_raw)
                data_line = None
                
                for line in out_decoded.split('\n'):
                    if "RESULTS:" in line:
                        data_line = line
                        break

                if data_line is None:
                    error_message = f"Could not find the 'RESULTS: ' line in the simulation output.\nFull Output:\n---\n{out_decoded}\n---"
                else:
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
                        error_message = f"The results line has {len(lines)} fields, but expected {(4 + num_robots)}.\nLine Found: '{data_line}'\nFull Output:\n---\n{out_decoded}\n---"
        
        except Exception as e:
            error_message = f"Code Exception during process communication. Error: {str(e)}"


    return process_has_end, sim_results, error_message

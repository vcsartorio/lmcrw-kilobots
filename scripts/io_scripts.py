from lxml import etree
import os
import csv
import pandas as pd

def readExperimentConfigFile(data_path):
    exp_config_options = f"{data_path}/exp_config.xml"
    exp_config = dict()

    try:
        tree = etree.parse(exp_config_options)
        root = tree.getroot()
        exp_config['alpha'] = float(root.get("alpha"))
        exp_config['rho'] = float(root.get("rho"))
        exp_config['num_robots'] = int(root.get("num_robots"))
        exp_config['arena_radius'] = float(root.get("arena_radius"))
        exp_config['simulation_time'] = int(root.get("simulation_time"))
        exp_config['max_trials'] = int(root.get("max_trials"))
        exp_config['evaluations'] = int(root.get("evaluations"))
        exp_config['num_threads'] = int(root.get("num_threads"))
        exp_config['kilobot_bias'] = True if root.get("kilobot_bias") == "True" else False
        exp_config['save_robots_fpt'] = True if root.get("save_robots_fpt") == "True" else False
    except Exception as e:
        print("Couldnt read config experiment options!\n" + str(e))

    return exp_config

def readLMCRWFptResults(folder, alpha_values, rho_values, num_robots, evaluations):
    print("Reading LMCRW results...")
    data_dict = dict()
    data_dict['Label'] = []
    data_dict['strategy'] = []
    data_dict['alpha'] = []
    data_dict['rho'] = []
    data_dict['Weibull Discovery Time'] = []
    data_dict['Discovery Time'] = []
    data_dict['Fraction Discovery'] = []

    for subdir, dirs, files in os.walk(os.getcwd() + folder):
        files.sort()

        for file_name in files:
            experiment_parameters = dict()
            experiment_parameters['n_robots'] = 1
            experiment_parameters['alpha'] = -1
            experiment_parameters['rho'] = -1
            experiment_parameters['evaluations'] = 1

            elements = file_name[:-4].split("_")
            experiment_parameters['strategy'] = elements[0]
            for e in elements[1:]:
                if e.endswith("R"):
                    experiment_parameters['n_robots'] = int(e.replace("R", ""))
                if e.endswith("a"):
                    experiment_parameters['alpha'] = float(e.replace("a", ""))
                if e.endswith("p"):
                    experiment_parameters['rho'] = float(e.replace("p", ""))
                if e.endswith("e"):
                    experiment_parameters['evaluations'] = int(e.replace("e", ""))

            if experiment_parameters['strategy'] != "crwlevy":
                continue
            if experiment_parameters['alpha'] not in alpha_values:
                continue
            if experiment_parameters['rho'] not in rho_values:
                continue
            if experiment_parameters['n_robots'] != num_robots:
                continue
            if experiment_parameters['evaluations'] != evaluations:
                continue
 
            print(f"Openning: {file_name}")
            with open(os.getcwd() + folder + file_name, "r") as dfile:
                try:
                    label_name = f"a:{experiment_parameters['alpha']} r:{experiment_parameters['rho']}"
                    read_tsv = csv.reader(dfile, delimiter="\t")
                    next(read_tsv, None)
                    for row in read_tsv:
                        data_dict['Label'].append(label_name)
                        data_dict['strategy'].append(experiment_parameters['strategy'])
                        data_dict['alpha'].append(experiment_parameters['alpha'])
                        data_dict['rho'].append(experiment_parameters['rho'])
                        data_dict['Weibull Discovery Time'].append(float(row[1])/32.0)
                        data_dict['Discovery Time'].append(float(row[2])/32.0)
                        data_dict['Fraction Discovery'].append(float(row[3]))
                    dfile.close()
                except Exception as e:
                    print(("Couldnt read results file: %s!\nException: " + str(e)) % (file_name))

    df = pd.DataFrame(data_dict)
    return df

def readRobotFptValues(folder, experiment_config):
    print(f"Reading robots values results from '{folder}'")
    robot_values = []

    for subdir, dirs, files in os.walk(os.getcwd() + folder):
        files.sort()
        
        for file_name in files:
            if "robots_values" not in file_name:
                continue

            experiment_parameters = dict()
            experiment_parameters['n_robots'] = 1
            experiment_parameters['alpha'] = -1
            experiment_parameters['rho'] = -1
            experiment_parameters['evaluations'] = 1

            elements = file_name.replace(".tsv", "").split("_")[2:]
            experiment_parameters['strategy'] = elements[0]
            for e in elements[1:]:
                if e.endswith("R"):
                    experiment_parameters['n_robots'] = int(e.replace("R", ""))
                if e.endswith("a"):
                    experiment_parameters['alpha'] = float(e.replace("a", ""))
                if e.endswith("p"):
                    experiment_parameters['rho'] = float(e.replace("p", ""))
                if e.endswith("e"):
                    experiment_parameters['evaluations'] = int(e.replace("e", ""))

            if experiment_parameters['strategy'] != "crwlevy":
                continue
            if experiment_parameters['alpha'] != experiment_config['alpha']:
                continue
            if experiment_parameters['rho'] != experiment_config['rho']:
                continue
            if experiment_parameters['n_robots'] != experiment_config['num_robots']:
                continue
            if experiment_parameters['evaluations'] != experiment_config['evaluations']:
                continue
 
            print(f"Openning: {file_name}")
            with open(os.getcwd() + folder + file_name, "r") as dfile:
                try:
                    read_tsv = csv.reader(dfile, delimiter="\t")
                    next(read_tsv, None)
                    for row in read_tsv:
                        robot_values.append([float(item) for item in row])
                    dfile.close()
                except Exception as e:
                    print(("Couldnt read results file: %s!\nException: " + str(e)) % (file_name))

    return robot_values
from lxml import etree

def readExperimentConfigFile(exp_config_options):
    exp_config = dict()

    try:
        tree = etree.parse(exp_config_options)
        root = tree.getroot()
        exp_config['alpha'] = float(root.get("alpha"))
        exp_config['rho'] = float(root.get("rho"))
        exp_config['num_robots'] = int(root.get("num_robots"))
        exp_config['arena_radius']= float(root.get("arena_radius"))
        exp_config['simulation_time']= int(root.get("simulation_time"))
        exp_config['max_trials'] = int(root.get("max_trials"))
        exp_config['evaluations'] = int(root.get("evaluations"))
        exp_config['num_threads'] = int(root.get("num_threads"))
        exp_config['kilobot_bias']= True if root.get("kilobot_bias") == "True" else False
    except Exception as e:
        print("Couldnt read config experiment options!\n" + str(e))

    return exp_config
import random
import time
import src.utils.Targets as Targets
import src.utils.LMCRW as LMCRW
import src.KilobotsSearchExperiment as KilobotsSearchExperiment
import scripts.io_scripts as io_scripts

generated_sim_config_folder = "simulation_config/generated_configs/"
exp_config_path = "simulation_config/exp_config.xml"

def performanceEvaluation():
    experiment_config = io_scripts.readExperimentConfigFile(exp_config_path)

    alpha = experiment_config['alpha']
    rho = experiment_config['rho']
    num_robots = experiment_config['num_robots']
    arena_radius = experiment_config['arena_radius']
    simulation_time = experiment_config['simulation_time']
    max_trials = experiment_config['max_trials']
    evaluations = experiment_config['evaluations']
    num_threads = experiment_config['num_threads']
    kilobot_bias = experiment_config['kilobot_bias']

    argos_path = generated_sim_config_folder + "kilobot_sim_%.3f_%d_%.1f_%.2f.argos" % (arena_radius, num_robots, alpha, rho)

    random.seed(15)
    targets_position = Targets.createTargetPosition(max_trials, False, arena_radius)

    lmcrw = LMCRW.LMCRW(alpha, rho, exp_id='0001')
    lmcrw.setPerformanceExperiment(num_robots, max_trials, round((arena_radius-0.025)*200), save_exp=True)

    print("Starting performance evaluation for LMCRW alpha:%.1f rho:%.2f.\nRobots: %d - Arena Radius: %.3fcm - Simulation Time: %d sec\nEvaluations: %d - Trials: %d - Bias: %s"
        % (alpha, rho, num_robots, arena_radius, simulation_time, evaluations, max_trials, kilobot_bias))
    
    start_time = time.time()
    for count_eva in range(evaluations):
        print("\nStarting %d trials (%d evaluation of %d):" % (max_trials, (count_eva+1), evaluations))
        experiment = KilobotsSearchExperiment.KilobotsExperiment(num_threads, num_robots, targets_position, arena_radius, simulation_time, kilobot_bias, argos_path)
        experiment.executeKilobotExperimentTrials(lmcrw)
        lmcrw.experiment_performance.resetResults()

    print("Time running: %s seconds" % (round(time.time() - start_time, 2)))


performanceEvaluation()
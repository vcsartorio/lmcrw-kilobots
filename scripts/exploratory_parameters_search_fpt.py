import random
import time
import src.utils.Targets as Targets
import src.utils.LMCRW as LMCRW
import src.KilobotsSearchExperiment as KilobotsSearchExperiment

generated_sim_config_folder = "simulation_config/generated_configs/"

def exploratorySearchForFptEvaluation(experiment_config):
    alpha_values = [1.2, 1.4, 1.6, 1.8, 2.0]
    rho_values = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9]
    
    num_robots = experiment_config['num_robots']
    arena_radius = experiment_config['arena_radius']
    simulation_time = experiment_config['simulation_time']
    max_trials = experiment_config['max_trials']
    evaluations = experiment_config['evaluations']
    num_threads = experiment_config['num_threads']
    kilobot_bias = experiment_config['kilobot_bias']

    random.seed(15)
    target_positions = Targets.createTargetPosition(max_trials, False, arena_radius)

    lmcrws_list = []
    for alpha in alpha_values:
        for rho in rho_values:
            lmcrw = LMCRW.LMCRW(alpha, rho, exp_id='0001')
            lmcrw.setPerformanceExperiment(num_robots, max_trials, round((arena_radius-0.025)*200), num_eval=evaluations, save_exp=True)
            lmcrws_list.append(lmcrw)

    print(f"Exploratory parameters search for the best first passage time of LMCRW (Robots: {num_robots} - Arena Radius: {arena_radius} cm - Simulation Time: {simulation_time} sec - Kilobot Bias: {kilobot_bias})")
    print(f"Alpha values: {','.join(map(str, alpha_values))}\nRho values: {','.join(map(str, rho_values))}\n")
    for lmcrw in lmcrws_list:
        start_time = time.time()
        print("Starting performance evaluation for LMCRW alpha:%.1f rho:%.2f.\nEvaluations: %d - Trials: %d " % (lmcrw.alpha, lmcrw.rho, evaluations, max_trials))
        for count_eva in range(evaluations):
            print("\nStarting %d trials (%d evaluation of %d):" % (max_trials, (count_eva+1), evaluations))
            argos_path = generated_sim_config_folder + "kilobot_sim_%.3f_%d_%.1f_%.2f.argos" % (arena_radius, num_robots, lmcrw.alpha, lmcrw.rho)
            experiment = KilobotsSearchExperiment.KilobotsExperiment(num_threads, num_robots, target_positions, arena_radius, simulation_time, kilobot_bias, argos_path)
            experiment.executeKilobotExperimentTrials(lmcrw)
            lmcrw.experiment_performance.resetResults()

        print(f"Time running for {evaluations} evaluations (alpha:{lmcrw.alpha} - rho:{lmcrw.rho}) = {round(time.time() - start_time, 2)} seconds.\n")
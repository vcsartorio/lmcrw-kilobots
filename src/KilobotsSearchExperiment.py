import src.ArgosSimulation as ArgosSimulation
import os
import time

class KilobotsExperiment(object):

    parameters_folder = "Data/"

    class KilobotSimulation(object):

        def __init__(self, exp_id, trial):
            unique_time = int(time.time() * 1000) % 10000 
            self.id = f"{exp_id:04}:{trial:03}_{unique_time:04}"
            self.exp_id = exp_id
            self.trial = trial
            self.simulation_total_time = -1

        def addSimulationProcess(self, process, argos_file):
            self.start_time = time.time()
            self.process = process
            self.argos_file = argos_file

        def simulationHasEnd(self):
            status = self.process.poll()
            if status is not None:
                self.simulation_total_time = time.time() - self.start_time
                return True
            
            return False

        def printSimulationResults(self, sim_results):
            print(f"Experiment {self.id} is finished after {self.simulation_total_time}s. Results: {sim_results['disc']} Discovery Time with {sim_results['frac disc']*100}%% Fraction discovery")

        def __repr__(self):
            return f'{self.exp_id:04}#{self.trial:03}'

    def __init__(self, num_threads, num_robots, targets_position, arena_radius, simulation_time, bias, argos_path):
        self.num_threads = num_threads
        self.num_robots = num_robots
        self.targets_position = targets_position
        self.arena_radius = arena_radius
        self.simulation_time = simulation_time
        self.kilobot_bias = bias
        self.argos_path = argos_path

    def changeTargetPositions(self, new_targets):
        self.targets_position = new_targets

    def executeKilobotExperimentTrials(self, experiment):
        simulation_pool = []

        while True:
            self.checkExperimentTrials(experiment, simulation_pool)
            self.checkSimulationPool(simulation_pool, experiment)
            experiment_end = self.checkExperimentFinalFitness(experiment)
            if experiment_end:
                break

        experiment.experiment_performance.printResult()

    def checkExperimentTrials(self, experiment, simulation_pool):
        if experiment.experiment_performance.num_trials < experiment.experiment_performance.max_trials:
            self.addSimulationOnPool(simulation_pool, experiment)

    def addSimulationOnPool(self, simulation_pool, experiment):
        if len(simulation_pool) < self.num_threads:
            trial = experiment.experiment_performance.num_trials
            sim_process = self.KilobotSimulation(int(experiment.exp_id), trial)
            
            process, temp_argos_file = ArgosSimulation.callArgosSimulation(self.argos_path, self.arena_radius, self.num_robots, self.simulation_time, sim_process.id)

            sim_process.addSimulationProcess(process, temp_argos_file)
            simulation_pool.append(sim_process)

            print(f'Running {int(experiment.exp_id)} Experiment -> {trial+1} trial! Active Threads: {len(simulation_pool)}')
            experiment.experiment_performance.num_trials += 1

    def checkSimulationPool(self, simulation_pool, experiment):
        process_has_end = False
        finished_process_id = -1

        for idx, simulation in enumerate(simulation_pool):
            process_end, sim_results, error_message = ArgosSimulation.checkProcessStatus(simulation, self.num_robots)

            if process_end:
                # 1. SIMULAÇÃO CONCLUÍDA COM SUCESSO
                if int(experiment.exp_id) == simulation.exp_id:
                    experiment.experiment_performance.setFitnessValues(sim_results['disc'], sim_results['inf'], sim_results['frac disc'], 
                        sim_results['frac inf'], sim_results['disc robots'], simulation.trial)
                    finished_process_id = idx
                    process_has_end = True

                    try:
                        os.remove(simulation.argos_file)
                    except OSError as e:
                        print(f"Warning: Failed to delete temporary config file {simulation.config_file}. Error: {e}")
                
                    simulation.printSimulationResults(sim_results)
                    break
                else:
                    print("Error! Simulation id dont belong to any experiment!")

            # 2. SIMULAÇÃO CONCLUÍDA COM ERRO
            elif error_message is not None:
                print(f"Unexpected error while running simulation: {simulation.id}. Reason:\n{error_message}")
                print(f"Simulation {simulation.id} will run again.")
                experiment.experiment_performance.num_trials -= 1 
                finished_process_id = idx 
                process_has_end = True
                break

        if process_has_end:
            del simulation_pool[finished_process_id]

    def checkExperimentFinalFitness(self, experiment):
        experiment_end = True
        if not experiment.experiment_performance.computed_final_fitness:
            experiment_end = False

        return experiment_end
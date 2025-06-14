import src.ArgosSimulation as ArgosSimulation
import os
import time

class KilobotsExperiment(object):

    parameters_folder = "Data/"

    class KilobotSimulation(object):

        def __init__(self, sim_id, trial, process):
            self.sim_id = sim_id
            self.trial = trial
            self.process = process
            self.start_time = time.time()
            self.simulation_total_time = -1

        def simulationHasEnd(self):
            status = self.process.poll()
            if status is not None:
                self.simulation_total_time = time.time() - self.start_time
                return True
            
            return False

        def checkSimulationTime(self):
            status = self.process.poll()
            if status is not None:
                self.simulation_total_time = time.time() - self.start_time
                if self.simulation_total_time > 120:
                    print("Simulation taking too long to finished")

        def printSimulationTotalTime(self):
            print(f'Total time: {self.simulation_total_time}s')

        def __repr__(self):
            return f'{self.sim_id:04}#{self.trial:03}'

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
            sim_id = experiment.exp_id + f'{trial:03}'
            process = ArgosSimulation.callArgosSimulation(self.argos_path, sim_id)
            simulation_process = self.KilobotSimulation(int(experiment.exp_id), trial, process)
            simulation_pool.append(simulation_process)
            print(f'Running {int(experiment.exp_id)} Experiment -> {trial+1} trial! Active Threads: {len(simulation_pool)}')
            # print(f'Running {int(network.exp_id)+1} Network -> {trial+1} trial! Threads: {simulation_pool}')
            experiment.experiment_performance.num_trials += 1

    def checkSimulationPool(self, simulation_pool, experiment):
        process_has_end = False
        process_idx = -1
        for idx, simulation in enumerate(simulation_pool):
            process_has_end, sim_results = ArgosSimulation.checkProcessStatus(simulation, self.num_robots)
            if process_has_end:
                if int(experiment.exp_id) == simulation.sim_id:
                    experiment.experiment_performance.setFitnessValues(sim_results['disc'], sim_results['inf'], sim_results['frac disc'], 
                        sim_results['frac inf'], sim_results['disc robots'], simulation.trial)
                    process_idx = idx
                    # print("%d Network %d trial is finished! %s scores: %d Discovery Time with %d%% Fraction discovery" % (simulation.sim_id+1, simulation.trial+1, 
                    #     network.bn_type, sim_results['disc'], sim_results['frac disc']*100))
                    # simulation.printSimulationTotalTime()
                    break
                if process_idx != -1:
                    break
                else:
                    print("Error! Simulation id dont belong to any experiment!")

        if process_has_end:
            del simulation_pool[process_idx]

    def checkExperimentFinalFitness(self, experiment):
        experiment_end = True
        if not experiment.experiment_performance.computed_final_fitness:
            experiment_end = False

        return experiment_end
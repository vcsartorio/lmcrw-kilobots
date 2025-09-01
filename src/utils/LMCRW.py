import src.utils.ExperimentPerformance as ExperimentPerformance
import os

class LMCRW:
    
    def __init__(self, alpha, rho, **kwargs):
        self.exp_id = kwargs.get('exp_id')
        self.alpha = alpha
        self.rho = rho

    def setPerformanceExperiment(self, num_robots, num_trials, arena_radius, sim_time, **kwargs):
        self.fpt_result = kwargs.get('fpt')
        self.experiment_performance = ExperimentPerformance.ExperimentPerformance(num_robots, num_trials, sim_time, exp_path=kwargs.get('exp_path'))
        if kwargs.get('save_exp'):
            self.experiment_date = kwargs.get('date')
            self.num_evaluations = kwargs.get('num_eval')
            self.performance_file = f"crwlevy_{num_robots}R_{self.alpha:.1f}a_{self.rho:.2f}p_{self.num_evaluations}e_{arena_radius}cm_{sim_time}sec.tsv"
            self.experiment_performance.initializeExperiment(self.performance_file, self.exp_id)

    def resetExperimentResults(self):
        self.experiment_performance.resetResults()



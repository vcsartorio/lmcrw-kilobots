import src.utils.ExperimentPerformance as ExperimentPerformance
import os

class LMCRW:
    
    def __init__(self, alpha, rho, **kwargs):
        self.exp_id = kwargs.get('exp_id')
        self.alpha = alpha
        self.rho = rho

    def setPerformanceExperiment(self, num_robots, num_trials, arena_radius, **kwargs):
        self.fpt_result = kwargs.get('fpt')
        self.experiment_performance = ExperimentPerformance.ExperimentPerformance(num_robots, num_trials, kwargs.get('exp_path'))
        if kwargs.get('save_exp'):
            self.experiment_date = kwargs.get('date')
            self.num_evaluations = kwargs.get('num_eval')
            self.performance_file = "LMCRW_%dR_%.1fa_%.2fp_%dcm_%de_%s.tsv" % (num_robots, self.alpha, self.rho, arena_radius, self.num_evaluations, self.experiment_date if self.experiment_date else "")
            self.experiment_performance.initializeExperiment(self.performance_file, self.exp_id)

    def resetExperimentResults(self):
        self.experiment_performance.resetResults()



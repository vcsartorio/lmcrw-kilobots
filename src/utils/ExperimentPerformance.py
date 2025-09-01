from ast import Num
import numpy as np
from numpy import save
from scipy.optimize import curve_fit
import scipy.special as sc
from matplotlib import pyplot as plt
from subprocess import Popen, PIPE
import csv
import os
import pandas as pd
import warnings

class ExperimentPerformance:

    def __init__(self, n_robots, n_trials, sim_time, **kwargs):
        self.num_robots = n_robots
        self.max_trials = n_trials
        self.max_simulation_time = sim_time
        self.experimental_folder = kwargs.get('exp_path')
        self.save_experiment = False
        self.computed_final_fitness = False
        self.trials_done = 0
        self.experiment_id = -1
        self.weibull_disc_evaluations_value = []
        self.startTimeValues()

    def initializeExperiment(self, performance_file, exp_id):
        self.final_performance_file = performance_file
        self.save_experiment = True
        self.experiment_id = int(exp_id)
        self.checkFinalPerformanceResultsFile()

    def startTimeValues(self):
        self.discovery_values = [0]*self.max_trials
        self.information_values = [0]*self.max_trials
        self.fraction_disc_values = [0]*self.max_trials
        self.fraction_inf_values = [0]*self.max_trials
        self.argos_simulations = [None]*self.max_trials
        self.discovery_robots_values = []
        self.num_trials = 0

    def setFitnessValues(self, disc, inf, frac_d, frac_i, disc_robot, trial_id):
        self.discovery_values[trial_id] = disc
        self.information_values[trial_id] = inf
        self.fraction_disc_values[trial_id] = frac_d
        self.fraction_inf_values[trial_id] = frac_i
        self.discovery_robots_values += disc_robot

        self.trials_done += 1
        if self.trials_done == self.max_trials:
            self.calculateFinalFitness()

    def calculateFinalFitness(self):
        self.discovery_time = sum(self.discovery_values)/len(self.discovery_values)
        self.information_time = sum(self.information_values)/len(self.information_values)
        self.fraction_discovery = sum(self.fraction_disc_values)/len(self.fraction_disc_values)
        self.fraction_information = sum(self.fraction_inf_values)/len(self.fraction_inf_values)
        self.weibull_discovery_time = self.calculateWeibullDiscoveryTime()
        self.computed_final_fitness = True
        self.weibull_disc_evaluations_value.append(self.weibull_discovery_time)

        if self.save_experiment:
            self.saveFinalPerformanceResult()     
    
    def calculateWeibullDiscoveryTime(self):
        fpt = np.asarray(self.discovery_robots_values)
        censored = fpt.size - np.count_nonzero(fpt)
        mean = self.discovery_time
        if censored == 0:
            return mean
        
        fpt = fpt[np.argsort(fpt.reshape(-1))]
        times_value = fpt[censored:].reshape(-1)
        if times_value.size == 0:
            print("AVISO: Nenhum robô encontrou o alvo. Não é possível calcular a média.")
            return np.nan

        F_empirical = self.estimatorKM(times_value, censored)

        # --- Início da Lógica Heurística para o bound_is ---
        kilobot_tick_per_seconds = 32
        bound_is = self.max_simulation_time *kilobot_tick_per_seconds
        max_iterations = 10
        target_ratio = 0.63

        for i in range(max_iterations):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore") 
                    popt_weibull, _ = curve_fit(
                        self.weib_cdf,
                        xdata=times_value,
                        ydata=np.squeeze(F_empirical),
                        bounds=([1e-9, 1e-9], [bound_is, 10]),
                        method='trf'
                )
                popt_weibull, _ = curve_fit(self.weib_cdf, xdata=times_value, ydata=np.squeeze(F_empirical), bounds=(0, [bound_is, 10]), method='trf')
            except RuntimeError as e:
                print(f"Erro no curve_fit: {e}. O bound pode ser muito restritivo. Interrompendo.")
                return np.nan
            
            # popt_weibull[0] is alpha and popt_weibull[1] is gamma
            alpha, gamma = popt_weibull
            current_ratio = alpha / bound_is
            # print("Alpha: %f - Gamma: %f" % (popt_weibull[0], popt_weibull[1]))
            # print(f"Ratio (Alpha / Bound): {current_ratio:.2%}")
            
            mean = sc.gamma(1 + (1. / gamma)) * alpha
            std_dev = np.sqrt(alpha ** 2 * sc.gamma(1 + (2. / gamma)) - mean ** 2)
            std_error = std_dev / np.sqrt(times_value.size)
            # print("Mean Weibull: %f - Standard Deviation: %f - Standard Error: %f" % (mean, std_dev, std_error))

            # Condição de parada: o alpha ocupa 63% ou menos do espaço de busca
            if current_ratio <= target_ratio+0.01:
                # print(f"Condição satisfeita ({current_ratio:.2%} <= {target_ratio:.2%}). Parando o ajuste.")
                break
            else:
                bound_is = alpha / target_ratio
                if i == max_iterations - 1:
                    print("\nAVISO: Número máximo de iterações atingido sem satisfazer a condição.")

        return mean

    def estimatorKM(self, data, censored):
        n_est = np.asarray(range(0, data.size))[::-1] + censored
        RT_sync = []
        for i in range(n_est.size):
            if len(RT_sync) == 0:
                RT_sync.append((n_est[i] - 1) / n_est[i])
            else:
                RT_sync.append(RT_sync[-1] * ((n_est[i] - 1) / n_est[i]))
        F = 1 - np.asarray(RT_sync).reshape(-1, 1)
        return F

    def weib_cdf(self, x, alpha, gamma):
        return (1 - np.exp(-np.power(x / alpha, gamma)))

    def getPerformanceResults(self):
        return (self.weibull_discovery_time, self.discovery_time, self.fraction_discovery, self.information_time, self.fraction_information)

    def resetResults(self):
        # print("Reseting results for experiment %d!" % (self.experiment_id))
        self.computed_final_fitness = False
        self.trials_done = 0
        self.discovery_values.clear()
        self.information_values.clear()
        self.fraction_disc_values.clear()
        self.fraction_inf_values.clear()
        self.argos_simulations.clear()
        self.discovery_robots_values.clear()
        self.checkFinalPerformanceResultsFile()
        self.startTimeValues()

    def weibull_plot(self, mean, std_dev, times_value, popt_weibull, F):
        fig, ax = plt.subplots(figsize=(20, 8), dpi=160, facecolor='w', edgecolor='k')
        '''Textbox with mu and sigma'''
        textstr = '\n'.join((
            r'$\mu=%.2f$' % (mean,),
            r'$\sigma=%.2f$' % (std_dev,)))

        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        # place a text box in upper left in axes coords
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

        y_weib = self.weib_cdf(times_value, popt_weibull[0], popt_weibull[1])
        error_weib = np.power(y_weib - np.squeeze(F), 2)
        plt.plot(times_value, y_weib, 'r', linewidth=5, label="Weibull Distribution")
        plt.plot(times_value, F, 'b', linewidth=5, label="K-M stats")
        plt.legend(loc=4)
        plt.ylim(0, 1)

        label = "Results for %s trials" % (self.max_trials)
        plt.title(label)
        plt.xlabel("Number of time steps")
        plt.ylabel("Probability of passing over the target")
        plt.show()

    def printResult(self):
        print("After %d trials, the results are: Weibull Discovery time: %d - Discovery time: %d - Fraction discovery: %.2f - Information time: %d - Fraction information: %.2f" % (self.max_trials, 
            self.weibull_discovery_time, self.discovery_time, self.fraction_discovery, self.information_time, self.fraction_information))

    def checkFinalPerformanceResultsFile(self):
        if self.save_experiment:
            if not os.path.exists(self.experimental_folder):
                os.makedirs(self.experimental_folder)
                
            file_path = self.experimental_folder + self.final_performance_file
            if os.path.exists(file_path):
                # elements = file_path.replace(".tsv", "").split("_")
                # max_evaluations = 500
                # for e in elements:
                #     if e.endswith("k"):
                #         max_evaluations = int(e.replace("k", ""))
                # result_file = pd.read_csv(self.experimental_folder + self.final_performance_file, '\t')
                # if len(result_file) >= max_evaluations:
                #     print("WARNING! In %s file, experiment has already perform %d trials! Quiting ..." % (self.final_performance_file, self.max_trials))
                #     exit(1)
                pass
            else:
                self.createFinalPerformanceFile()

    def createFinalPerformanceFile(self):
        print("Creating %s ..." % (self.final_performance_file))
        with open(self.experimental_folder + self.final_performance_file, 'wt') as out_file:
            try:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                tsv_writer.writerow(['Id', 'Weibull Discovery Time', 'Discovery Time', 'Fraction Discovery', 'Information Time', 'Fraction Information'])
                out_file.close()
            except Exception as e:
                print("Couldnt create final performance results file!\n" + str(e))
        
    def saveFinalPerformanceResult(self):
        if self.experiment_id == -1:
            self.experiment_id = len(pd.read_csv(self.experimental_folder + self.final_performance_file, '\t')) + 1
        with open(self.experimental_folder + self.final_performance_file, 'a') as out_file:
            try:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                tsv_writer.writerow([self.experiment_id, round(self.weibull_discovery_time, 0), round(self.discovery_time, 0), round(self.fraction_discovery, 4), 
                    round(self.information_time, 0), round(self.fraction_information, 4)])
                out_file.close()
            except Exception as e:
                print("Couldnt save final performance results!\n" + str(e))

    def saveAllRobotsFptValues(self):
        all_robots_file = "robots_values_" + self.final_performance_file
        if self.experiment_id == -1:
            self.experiment_id = len(pd.read_csv(self.experimental_folder + all_robots_file, '\t')) + 1
        with open(self.experimental_folder + all_robots_file, 'wt') as out_file:
            try:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                for trial in np.arange(1, self.max_trials+1):
                    first_robot = (trial-1)*self.num_robots
                    last_robot = trial*self.num_robots
                    tsv_writer.writerow(self.discovery_robots_values[first_robot:last_robot])
                out_file.close()
            except Exception as e:
                print("Couldnt save all robots fpt values!\n" + str(e))

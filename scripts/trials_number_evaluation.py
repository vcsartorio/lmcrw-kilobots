import random
import time
import src.utils.Targets as Targets
import src.utils.LMCRW as LMCRW
import src.KilobotsSearchExperiment as KilobotsSearchExperiment
import scripts.io_scripts as io_scripts
import numpy as np
from scipy.optimize import curve_fit
import scipy.special as sc
from matplotlib import pyplot as plt

generated_sim_config_folder = "simulation_config/generated_configs/"
experiment_folder = "Fpt-performance"

def plotResultsForDifferentMaxTrials(robot_values):
    print("Plotting results for different max trials...")
    plt.style.use('seaborn-v0_8-whitegrid')
    bound_list = [30000, 50000, 75000]
    for bound in bound_list:
        print(f"\nBound for calculating Weibull is {bound}:")
        fig, ax = plt.subplots(figsize=(12, 8))

        list_all_robots_values = [item for sublist in robot_values for item in sublist]
        fpt = np.asarray(list_all_robots_values)
        censored = fpt.size - np.count_nonzero(fpt)
        if censored != 0:
            fpt = fpt[np.argsort(fpt.reshape(-1))]
            times_value = fpt[censored:].reshape(-1)
            F_empirical = estimatorKM(times_value, censored)
            ax.plot(times_value, F_empirical, 'o', color='black', markersize=6, label='Dados Empíricos (Kaplan-Meier)')

        number_of_trials = [8,20,30,50,75,100]
        for trials in number_of_trials:
            print(f"Number of trials:{trials}")
            list_robots_values = [item for sublist in robot_values[:trials] for item in sublist]
            fpt = np.asarray(list_robots_values)
            print(f"Discovery Time:{fpt.mean()}")
            print(f"Fraction Discovery:{np.count_nonzero(fpt)/fpt.size}")
            alpha, gamma, weibull = calculateWeibullDiscoveryTime(fpt, bound)
            print(f"Mean Weibull Discovery Time for {trials} trials: {weibull:.2f}\n--------------------")
            x_curve = np.linspace(0, 200000, 500)
            y_curve = calculateWeibullCdf(x_curve, alpha, gamma)
            ax.plot(x_curve, y_curve, label=f'Trials:{trials}-Weibull:{weibull:.2f}', linewidth=2.5, alpha=0.7)

        # 3. Embelezamento do gráfico
        ax.set_title('Curva de Weibull para diferentes trials', fontsize=16)
        ax.set_xlabel('Tempo de Descoberta (passos)', fontsize=12)
        ax.set_ylabel('Probabilidade Cumulativa (CDF)', fontsize=12)
        ax.legend(title='Legenda', fontsize=10)
        ax.set_xlim(0, 200000)
        ax.set_ylim(0, 1.05)

        plt.show()
        print(f"\n=============================")

def calculateWeibullDiscoveryTime(discovery_robots_values, bound_is):
    fpt = np.asarray(discovery_robots_values)
    censored = fpt.size - np.count_nonzero(fpt)
    if censored == 0:
        return 0,0,fpt.mean()
    fpt = fpt[np.argsort(fpt.reshape(-1))]
    times_value = fpt[censored:].reshape(-1)

    F = estimatorKM(times_value, censored)

    popt_weibull, _ = curve_fit(calculateWeibullCdf, xdata=times_value, ydata=np.squeeze(F), bounds=(0, [bound_is, 10]), method='trf')
    mean = sc.gamma(1 + (1. / popt_weibull[1])) * popt_weibull[0]
    std_dev = np.sqrt(popt_weibull[0] ** 2 * sc.gamma(1 + (2. / popt_weibull[1])) - mean ** 2)
    std_error = std_dev / np.sqrt(times_value.size)

    return popt_weibull[0], popt_weibull[1], mean

def estimatorKM(data, censored):
    # Versão mais eficiente e numericamente estável do Kaplan-Meier
    n_individuals = data.size + censored
    # np.unique lida com múltiplos robôs encontrando o alvo no mesmo instante de tempo
    times, event_counts = np.unique(data, return_counts=True)
    
    at_risk = np.array([n_individuals - np.sum(event_counts[:i]) for i in range(len(event_counts))])
    
    survival_prob = np.cumprod((at_risk - event_counts) / at_risk)
    
    # Precisamos mapear as probabilidades de volta para o array 'data' original
    # que pode ter tempos duplicados.
    prob_map = {t: p for t, p in zip(times, survival_prob)}
    full_survival_prob = np.array([prob_map[t] for t in data])

    F = 1 - full_survival_prob.reshape(-1, 1)
    return F

def calculateWeibullCdf(x, alpha, gamma):
    return (1 - np.exp(-np.power(x / alpha, gamma)))

def evaluateDifferentTrialsResults(experiment_config, data_path):
    experiment_path = f"/{data_path}{experiment_folder}/"
    robot_values = io_scripts.readRobotFptValues(experiment_path, experiment_config)
    plotResultsForDifferentMaxTrials(robot_values)

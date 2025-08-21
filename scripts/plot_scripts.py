import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import scripts.io_scripts as io_scripts

folder = "/data/Fpt-performance/"
alpha_values = [1.2, 1.4, 1.6, 1.8, 2.0]
rho_values = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9]

def plotHeatMapParametersSearch(experiment_config):
    num_robots = experiment_config['num_robots']
    evaluations = experiment_config['evaluations']
    arena_radius = experiment_config['arena_radius']
    simulation_time = experiment_config['simulation_time']
    max_trials = experiment_config['max_trials']
    num_threads = experiment_config['num_threads']
    kilobot_bias = experiment_config['kilobot_bias']

    df = io_scripts.readLMCRWFptResults(folder, alpha_values, rho_values, num_robots, evaluations)
    print(df)
    plots_dict = dict()
    plots_dict['Weibull Discovery Time'] = {'df':df.pivot_table(index='alpha', columns='rho', values='Weibull Discovery Time'), 'cmap':"Purples_r"}
    plots_dict['Discovery Time'] = {'df':df.pivot_table(index='alpha', columns='rho', values='Discovery Time'), 'cmap':"Blues_r"}
    plots_dict['Fraction Discovery'] = {'df':df.pivot_table(index='alpha', columns='rho', values='Fraction Discovery'), 'cmap':"Greens_r"}

    for keys, values in plots_dict.items():
        ax = sns.heatmap(values['df'], annot=True, fmt=".2f", cmap=values['cmap'], cbar_kws={'label':f"{keys}"})
        ax.invert_yaxis()
        plt.title(f"LMCRW experiment w/ {num_robots}R - {evaluations} evaluations of 50 trials")
        plt.show()

def plotBoxplotParametersSearch(experiment_config):
    num_robots = experiment_config['num_robots']
    evaluations = experiment_config['evaluations']
    arena_radius = experiment_config['arena_radius']
    simulation_time = experiment_config['simulation_time']
    max_trials = experiment_config['max_trials']
    num_threads = experiment_config['num_threads']
    kilobot_bias = experiment_config['kilobot_bias']

    df = io_scripts.readLMCRWFptResults(folder, alpha_values, rho_values, num_robots, evaluations)
    
    x_value = "Label"
    y_value = "Weibull Discovery Time"
    sns.set_style("whitegrid")
    ax = sns.boxplot(x=x_value, y=y_value, hue="alpha",linewidth=1, showfliers=True, dodge=False, data=df)

    ax.set_title(f"LMCRW experiment w/ {num_robots}R - {evaluations} evaluations of 100 trials")
    ax.set_xlabel("LMCRW", fontsize=15)
    if y_value == "Fraction Discovery":
        ax.set_ylabel("Fraction Discovery", fontsize=15)
        f = lambda x, pos: f'{x*100:,.0f}%'
        ax.yaxis.set_major_formatter(FuncFormatter(f))
    else:
        ax.set_ylabel("First passage time " + r'($t_f$)', fontsize=15)
        # f = lambda x, pos: f'{x/10**3:,.0f}K'

    fig = plt.gcf()
    fig.set_size_inches(12, 5)
    fig.tight_layout()
    plt.legend(loc='best', title= "alpha", fontsize=11)
    plt.xticks(fontsize=12)
    plt.xticks([])
    plt.show()



import sys
import time
import src.utils.Targets as Targets
import src.utils.LMCRW as LMCRW
import src.KilobotsSearchExperiment as KilobotsSearchExperiment
import scripts.io_scripts as io_scripts
import scripts.fpt_evaluation as fpt_evaluation
import scripts.exploratory_parameters_search_fpt as exploratory_parametes_search_fpt
import scripts.plot_scripts as plot_scripts

exp_config_path = "simulation_config/exp_config.xml"

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Not enough arguments!")
    else:
        script_name = str(sys.argv[1])
        experiment_config = io_scripts.readExperimentConfigFile(exp_config_path)
        try:
            if script_name == "fpt_evaluation":
                fpt_evaluation.performanceEvaluation(experiment_config)
            if script_name == "search_par_fpt":
                exploratory_parametes_search_fpt.exploratorySearchForFptEvaluation(experiment_config)
            if script_name == "plot_results":
                if sys.argv[2] == "heatmap":
                    plot_scripts.plotHeatMapParametersSearch(experiment_config)
                if sys.argv[2] == "boxplot":
                    plot_scripts.plotBoxplotParametersSearch(experiment_config)

        except Exception as e:
            print(e)

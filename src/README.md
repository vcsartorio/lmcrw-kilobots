# src folder

creation : Amaury Camus   
mail : amaury.camus92@gmail.com   
supervision : Vito Trianni   

## Behaviors folder
The behaviors (native kilobot code) should work the same exact way for
both real and simulation.   
In the folder is also a **CMakeLists.txt** that compiles the behaviors for **ARGoS** and generates argos config files.  
It is in this cmakelists.txt that you can specify the range for alpha, rho and the number of robots.   


## cmake folder
This folder is used to set cmake to compile for ARGoS. Do not delete or modify it if you don't know what you are doing. 

## kilobots folder
This folder contains the code to compile behaviors for **real robots**.    
The Makefile contains the real compilation instructions, but to make it easy to build everything, there is a CMakelist.txt that just calls the makefile.

The content of this folder **shoud not be modified** except for the Makefile, to add compilation of new behaviors.    

**Warning** The Makefile isn't very well designed, and is very project-architecture dependent, meaning that if you move things around, you might have to change paths inside it if you don't want to break it.   

## loop_functions folder 
I added loop functions (ci_kilobot_loop_functions). They are compiled against the rest of the kilobot simulation plugin, but are use-dependant and don't belong in the plugin.

## CMakelists.txt
This CMakelists.txt initializes variables and calls the compilation of:
- The argos-kilobot plugin
- The behaviors for compilation (as well as the generation of corresponding ARGoS config files)
- The behaviors for real kilobots (with the Makefile as seen previously)

Normaly, it should not be modified, except if you have to add include or library paths. Be advised, adding include path and lib path in the Cmakes will not put them in the scope of the Makefile (in the makefile, path are also added when needed). There might be a better and more elegant solution.

## What is produced
In the build directory, you will find:
- behaviors_real : a folder containing all compiled bahaviors for real Kilobots, as parameterized in src/kilobots/Makefile
- behaviors_simulation : a folder containing all compiled behaviors for ARGoS kilobots, as parameterized in src/behaviors/CMakeLists.txt
- loop_functions/libloop_function.so : The library containing our custom loop functions for ARGoS : it is automatically called in the config files 

In the simulation_config directory:
- All the generated configuration files in generated_configs.
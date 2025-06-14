## Description
This repository can run experiment for Kilobots using ARGoS Simulation and LMCRW as random walk.

## src folder
It contains all the code. See internal README for more information  

## simulation_config folder
It contains the ARGoS config files, which will be generated on building (see below and in the src/README.md)

# Build and use

### Dependancies
Prior to using this work, you should have installed:

- Argos3 (from sources : https://github.com/ilpincy/argos3 , installed in usr/local)
- Argos3 kilobot plugin (from sources : https://github.com/ilpincy/argos3-kilobot , installed in usr/local)

The current state of this works allows me to make it work on ubuntu 16.04 and 14.04, though I don't know for mac OS.

### Building
At the root folder (same level as src):  
`mkdir build` (if it doesn't already exists)    
`cd build`   
`cmake ../src`   
`make`   

It should compile everything.     
- Thanks to the cmakelists.txt in behaviors, with its for loops, you can specify the whole range of parameters for which you want to run experiments. Is should generate:  
     - The binary behavior files in build/behaviors_simulation
     - The config files in simulation_config/generated_configs
- The .hex files needed for real kilobots are in build/behaviors_real


### Launching a simulation
Steps:
- Make sure you have argos3 installed (typing `which argos3` should give the path to the executable)  
- Make sure you are in the root folder
- From the root folder, use the command `argos3 -c simulation_config/MY_CONFIG.argos`

### Lauching multiple simulation
Using main.py script you can run multiple simulations at once. You just need to configure `simulation_config/exp_config.xml` file and then run `python3 main.py`


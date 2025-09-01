# THIS IS ONLY FOR SIMULATION -> TODO deport it to a behaviors_simulation folder

Set(REAL 0)
if(ARGOS_BUILD_FOR_SIMULATOR)
#include_directories(${CMAKE_SOURCE_DIR}/plugins/robots/kilobot/control_interface)
include_directories(/usr/local/include/argos3/plugins/robots/kilobot/control_interface /usr/local/include/argos3/plugins/robots/kilobot/simulator)
    add_custom_target(config_file_viz
                    ALL
                   COMMAND python3 src/generate_config_visual.py simulation_config
                   WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/..)


    foreach(crw 0.00 0.15 0.30 0.45 0.60 0.75 0.90 0.95 0.99)
        foreach(levy 1.0 1.2 1.4 1.6 1.8 2.0)
            add_executable(CRWLEVY_${levy}_${crw} CRWLEVY.c )
            target_link_libraries(CRWLEVY_${levy}_${crw} argos3plugin_simulator_kilolib rt m)
            target_compile_definitions(CRWLEVY_${levy}_${crw} PRIVATE -DLEVY_EXPONENT=${levy} -DCRW_EXPONENT=${crw} -DMAX_TIME=100000000)
            add_custom_target(config_file_${levy}_${crw}
                ALL
                COMMAND python3 src/generate_configs.py simulation_config ${levy} ${crw}
                WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/..)

        endforeach(levy)
    endforeach(crw)
  
      add_executable(Target Target.c)
  target_link_libraries(Target argos3plugin_simulator_kilolib rt m)

endif(ARGOS_BUILD_FOR_SIMULATOR)



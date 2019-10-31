This repository contains a show-case of python scripts I developed for different purposes:

Fig1_plot_PB_2D_COLORMESH.py: Plots the rate of error of geopotential height at Z500 (a fundamental field on mid-latitude meteorology) for all forecast lead times and initialization times to highlight validation times where errors are more likely to occur. This plot is the basis for the Predictability barriers idea, introduced in Sanchez et al. 2019 (in preparation)

output_models.py: Reads a database of location and intensity of forecasted tropical cyclones (TC), and outputs a chosen TC with a specific time format

plot_Int_traj.py: Plots trajectory, Intensity and 10m wind speed of a given TC from the output produced by the script above. 

plot_dom_suite.py: Plots the domains specified in the cylc-rose suite of nested regional models, reading the attribute rose-suite.conf , which containing the relevant variables

PR of inputs for these scripts, as well as their outputs, may be restricted. Therefore they are not included in this repository

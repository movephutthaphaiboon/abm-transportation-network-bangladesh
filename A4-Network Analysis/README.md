# README File

Created by: EPA133a Group 16

|    Name     | Student Number |
| :---------: | :------------- |
| Rachel Delvin Sutiono | 6284736        |
|  Celia Martínez Sillero  | 6222102         |
| Daniela Ríos Mora | 6275486       |
| Thunchanok Phutthaphaiboon| 6141153        |
| Yao Wang | 6157513         |



## Introduction

In the folder (EPA133a-G16-A4),  can find place group 16's lab submission for the Assignment 4.

This README file is to help a first-time user understand what it is about and how they might be able to use it.
 

## Purpose and objective of this project

Expanding on our previous work, we model two different evaluation metrics to support 
the World Bank's study on the criticality and vulnerability of roads N1, N2,
and their main branches in Bangladesh.


## Structure

The following submission is provided with the following structure:
Structure inside this ZIP file: 

    Folder EPA133a-G16-A4

        Subfolder data
            Subfolder raw
               -_roads3.csv
                -BMMS_overview.xlsx
                -N1.traffic.htm
                -N102.traffic.htm
                -N104.traffic.htm
                -N105.traffic.htm
                -N106.traffic.htm
                -N2.traffic.htm
                -N204.traffic.htm
                -N207.traffic.htm
                -N208.traffic.htm
                -demo_100_complete.csv
                -demo_100_complete_with_traffic.csv
                -2011-BGD-L4.csv    
                Subfolder floods
                    -bgd_nhr_rivererosion_barc
                    -bgd_nhr_floods_sparsso.cpg
                    -bgd_nhr_floods_sparsso.dbf
                    -bgd_nhr_floods_sparsso.prj
                    -bgd_nhr_floods_sparsso.sbn
                    -bgd_nhr_floods_sparsso.sbx
                    -bgd_nhr_floods_sparsso.shp
                    -bgd_nhr_floods_sparsso.shx
                    -demo.png
                    -demo_100_traffic.csv
                    -demo_100_with_traffic copy.csv
                    -demo_with_intersection.csv
                    -df_road_N1andN2.csv
                    -flood.png
                    -floodnet.png

                Subfolder shp
                    -bgd_admbnda_adm4_bbs_20201113.CPG
                    -bgd_admbnda_adm4_bbs_20201113.dbf
                    -bgd_admbnda_adm4_bbs_20201113.prj
                    -bgd_admbnda_adm4_bbs_20201113.sbn
                    -bgd_admbnda_adm4_bbs_20201113.sbx
                    -bgd_admbnda_adm4_bbs_20201113.shp
                    -bgd_admbnda_adm4_bbs_20201113.shx

        Subfolder processed
                    -N102_traffic.csv
                    -N104_traffic.csv
                    -N105_traffic.csv
                    -N106_traffic.csv
                    -N1_traffic.csv
                    -N204_traffic.csv
                    -N207_traffic.csv
                    -N208_traffic.csv
                    -N2_traffic.csv
                    -demo_100.csv
                    -demo_100_complete.csv
                    -demo_100_with_traffic.csv
                    -demo_100_with_traffic_and_pop_density


      Subfolder img
                -Network_Plot_with_pop_quantile.png
                -pop_density.png
                -pop_density_close_up.png 
                - demo-1.png
                - demo-2.png
                - demo-3.png
                - demo-4.png
                - N1.png
                - N1N2.png

        Subfolder model
            Subfolder Continuous Space
                -continuous_space.py
                -continuous_space_viz.py
            -model.py
            -components.py
            -model_viz.py
            -exploring.py
            -model_run.py
            -requirements.txt

        Subfolder notebook
            -1_CleanDemoFile.ipynb 
            -2_ScrapeTrafficData.ipynb
            -3_CombineDemoAndTrafficData.ipynb
            -4_CreateDemoFile_Network.ipynb
            -5_network_bridge_rank.ipynb
            -Explore flood risk.ipynb
            -Vulnerability analyses.ipynb

      Subfolder report
            -EPA133a-G16-A4-Report.pdf

      -README.md (this file)


## Main Files

- [1_CleanDemoFile.ipynb](notebook/1_CleanDemoFile.ipynb): Start of Metric 1. Takes df_road_N1andN2.csv and filters all roads to only the ones of interest. It outputs a new csv.


- [2_ScrapeTrafficData.ipynb](notebook/2_ScrapeTrafficData.ipynb): Scrapes the traffic data from the website as input. Saves a csv with traffic per road.

- [3_CombineDemoAndTrafficData.ipynb](notebook/3_CombineDemoAndTrafficData.ipynb): End of Metric 1. Combines two previous sets of outputs into one csv file and calculates random sink probability, truck generation frequency, and normalises truck data.

- [4_CreateDemoFile_Network.ipynb](notebook/4_CreateDemoFile_Network.ipynb): Beginning of Metric 2. Creates an economic activity proxy score per infrastructure class instance.

- [5_network_bridge_rank.ipynb](notebook/5_network_bridge_rank.ipynb): End of Metric 2. Calculate betweeness centrality using as graphs's weights a 
combination of economic proxy score and length as weight.

- [Explore flood risk.ipynb](notebook/Explore flood risk.ipynb): explores the flood risk probability

- [Vulnerability analyses.ipynb](notebook/Vulnerability analyses.ipynb): plots interesting visualisations of vulnerability and flood risk.
- 
- [model.py](model/model.py): Contains the model `BangladeshModel` which is a subclass of Mesa `Model`.  It reads a `csv` file with specific format for (transport) model generation.In this case it reads [demo_with_intersection.csv](data/processed/demo_with_intersection.csv) which is the file with the information of road N1.

- [components.py](model/components.py): Contains the model component definitions for the (main) model. 

- [model_viz.py](model/model_viz.py): Sets up the visualization; uses the `SimpleCanvas` element defined. Calls the model. Run the visualization server.

- [model_run.py](model/model_run.py): Sets up the model run (conditions). Calls the model. Run the simulation without visualization.

- [requirements.txt](Requirements.txt): Contains the required libraries to run the model.


- [ContinuousSpace](model/ContinuousSpace): The directory contains files needed to visualize Python3 Mesa models on a continuous canvas with geo-coordinates, a functionality not contained in the current Mesa package.

- [ContinuousSpace/SimpleContinuousModule.py](model/ContinuousSpace/SimpleContinuousModule.py): Defines `SimpleCanvas`, the Python side of a custom visualization module for drawing objects with continuous positions. This is a slight adaptation of the Flocker example provided by the Mesa project.

- [ContinuousSpace/simple_continuous_canvas.js](model/ContinuousSpace/simple_continuous_canvas.js): JavaScript side of the `SimpleCanvas` visualization module. It takes the output generated by the Python `SimpleCanvas` element and draws it in the browser window via HTML5 canvas. It can draw circles and rectangles. Both can have text annotation. 

- [README.md](README.md): This file.


## How to Use


# METRIC 1: Simulation-based approach
The main file for the user to get the results is [model_run.py](model/model_run.py). This file contains the code to run the simulation model without visualization. 

1. Run the notebook [1_CleanDemoFile.ipynb](notebook/1_CreateDemoFile.ipynb) to filter the demo to only N1, N2 and secondary roads longer than 25km.
 
    Input: df_road_N1andN2.csv
    Output:
          demo_100.csv

2. Run this notebook to scrape traffic data from the HTML files and saves it as CSV files so we can use it easily.
    Input: htms files from the data/raw folder
   Output:           -N102_traffic.csv
                    -N104_traffic.csv
                    -N105_traffic.csv
                    -N106_traffic.csv
                    -N1_traffic.csv
                    -N204_traffic.csv
                    -N207_traffic.csv
                    -N208_traffic.csv
                    -N2_traffic.csv
                    -demo_100.csv
                    -demo_100_complete.csv
                    -demo_100_with_traffic.csv



3. Run This notebook puts the road data (demo_100.csv) and traffic data (like N1_traffic.csv) together. It also calculates the necessary metrics used in the model:
        -truck_generation_frequency: how often trucks are created at each sourcesink
        -sink_selection_probability: how likely each sourcesink is chosen as a destination
        -heavy_truck_normalized: how much heavy truck traffic there is on each road

   Input: demo_100.csv, N1_traffic.csv, N2_traffic.csv, N102_traffic.csv, N104_traffic.csv, N105_traffic.csv, N106_traffic.csv, N204_traffic.csv, N207_traffic.csv, N208_traffic.csv

   Output: demo_100_with_traffic.csv

4. Run the notebook [Explore flood risk.ipynb](notebook/Explore flood risk.ipynb) to extract flood risk data

   Input: flood shape file in data/raw/floods folder, [bgr_nhr_floods_sparsso.shp](data/raw/floods/bgd_nhr_floods_sparsso.shp)
          [df_road_N1andN2.csv](data/processed/df_road_N1andN2.csv)
          [demo_100_with_traffic.csv](data/processed/demo_100_with_traffic.csv)
5. 
   Output: [demo_100_complete.csv](data/processed/demo_100_complete.csv) with the flood risk data added to it.

5. Run model_run.py to run the model. This file contains the code to run the simulation model without visualization. 
It reads the demo_with_intersection.csv file and runs the simulation for 4320 ticks. 
The output is a csv file with the results of the simulation.Each scenario is run for 100 replications using the same set of random seeds to ensure that results are comparable across scenarios. For each run, the average driving
time is recorded, along with a dictionary of bridge IDs and their corresponding accumulated delay times. 

6. Run the notebook [Vulnerability analyses.ipynb](notebook/Vulnerability analyses.ipynb) to plot the results of the simulation.



# METRIC 2: Network-based approach

1. Run notebook [4_CreateDemoFile_Network.ipynb](notebook/4_CreateDemoFile_Network.ipynb) to create the demo file for the network model.
    Input: [WB data](data/raw/2011-BGD-L4.csv)  
            [demo_100_complete_with_traffic.csv](data/processed/demo_100_complete_with_traffic.csv)
            [Bangladesh shapefiles](data/raw/shp)
2. 
    Output: [demo_100_with_traffic_and_pop_density.csv](data/processed/demo_100_with_traffic_and_pop_density.csv)
2. Run notebook [5_network_bridge_rank.ipynb](notebook/5_network_bridge_rank.ipynb) to calculate the bridge rank and plot the results.
        
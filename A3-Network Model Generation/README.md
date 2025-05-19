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

In the folder (EPA133a-G16-A3),  can find place group 16's lab submission for the Assignment 3.

This README file is to help a first-time user understand what it is about and how they might be able to use it.
 

## Purpose and objective of this project

Expanding on our previous work, we model goods transport along N1, N2, and their major side roads, automatically generating road and bridge components from the infrastructure data. Through this assignment, we aim to build a transport simulation that provides valuable insights into the effects of infrastructure failures on traffic flow.

## Structure

The following submission is provided with the following structure:
Structure inside this ZIP file: 

    Folder EPA133a-G16-A3

        Subfolder data
            Subfolder raw
               -_roads3.csv
                -BMMS_overview.xlsx
                -demo-4.csv

            Subfolder processed
                -demo_with_intersection.csv (current data for the model)

            Subfolder experiment
                -merged_scenarios_summary.csv
                -scenario0.csv
                -scenario1.csv
                -scenario2.csv
                -scenario3.csv
                -scenario4.csv
      Subfolder img
                -average_broken_bridges_per_scenario.png
                -count of broken bridges per scenario and seed.png
                -distribution_average_driving_time_per_scenario.png   
                -distribution_average_effective_speed_per_scenario.png
                -merged_scenarios_summary.csv 
            Subfolder sample
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
            -analysis.ipynb 
            -CreateDemoFile.ipynb

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
            -analysis.ipynb 
            -average_broken_bridges_per_scenario.png
            -count of broken briges per scenario and seed.png
            -distribution_average_driving_time_per_scenario.png   
            -distribution_average_effective_speed_per_scenario.png
            -merged_scenarios_summary.csv   

    -README.md

      Subfolder report
            -EPA133a-G16-A3-Report.pdf



      -README.md (this file)


## Main Files

- [model.py](model/model.py): Contains the model `BangladeshModel` which is a subclass of Mesa `Model`.  It reads a `csv` file with specific format for (transport) model generation.In this case it reads [demo_with_intersection.csv](data/processed/demo_with_intersection.csv) which is the file with the information of road N1.

- [components.py](model/components.py): Contains the model component definitions for the (main) model. 

- [model_viz.py](model/model_viz.py): Sets up the visualization; uses the `SimpleCanvas` element defined. Calls the model. Run the visualization server.

- [model_run.py](model/model_run.py): Sets up the model run (conditions). Calls the model. Run the simulation without visualization.

- [requirements.txt](Requirements.txt): Contains the required libraries to run the model.

- [analysis.py](notebook/analysis.ipynb): Contains the code to visualize the boxplot of the nine scenarios.
- 
- [CreateDemoFile.ipynb](notebook/CreateDemoFile.ipynb): Contains the code to create the demo_with_intersection.csv file.

- [README.md](README.md): This file.

- [ContinuousSpace](model/ContinuousSpace): The directory contains files needed to visualize Python3 Mesa models on a continuous canvas with geo-coordinates, a functionality not contained in the current Mesa package.

- [ContinuousSpace/SimpleContinuousModule.py](model/ContinuousSpace/SimpleContinuousModule.py): Defines `SimpleCanvas`, the Python side of a custom visualization module for drawing objects with continuous positions. This is a slight adaptation of the Flocker example provided by the Mesa project.

- [ContinuousSpace/simple_continuous_canvas.js](model/ContinuousSpace/simple_continuous_canvas.js): JavaScript side of the `SimpleCanvas` visualization module. It takes the output generated by the Python `SimpleCanvas` element and draws it in the browser window via HTML5 canvas. It can draw circles and rectangles. Both can have text annotation. 




## How to Use

The main file for the user to get the results is [model_run.py](model/model_run.py). This file contains the code to run the simulation model without visualization. 

1. Run the notebook [CreateDemoFile.ipynb](notebook/CreateDemoFile.ipynb) to create the demo_with_intersection.csv file. This file creates the csv with the information of the road N1.
 
    Input: [_roads3.csv](data/raw/_roads3.csv), [BMMS_overview.xlsx](data/raw/BMMS_overview.xlsx)
    Output:
           [demo_with intersection.csv](data/processed/demo_with_intersection.csv).

2. Run model_run.py to get the results of the simulation. The results of each step will be printed in the console. 
 
    Output:
                Results per step in terminal,(__Note: to reduce computational time, we commented the Vehicle print functions__)
                [scenario0.csv](experiment/scenario0.csv),
                [scenario1.csv](experiment/scenario1.csv),
                [scenario2.csv](experiment/scenario2.csv),
                [scenario3.csv](experiment/scenario3.csv),
                [scenario4.csv](experiment/scenario4.csv),


3. To visualize the results: run the [analysis.ipybn](notebook/analysis.ipynb) file. This file contains the code to visualize the boxplot of the nine scenarios.
    Input: all 4 csv scenario files. (see 2.)
    Output: [average_broken_bridges_per_scenario.png](img/average_broken_bridges_per_scenario.png)
            [count of broken bridges per scenario and seed.png](img/Count of Broken Bridges per Scenario and Seed.png)
            [distribution_average_driving_time_per_scenario.png](img/distribution_average_driving_time_per_scenario.png)   
            [distribution_average_effective_speed_per_scenario.png](img/distribution_average_effective_speed_per_scenario.png)
            [merged_scenarios_summary.csv](img/merged_scenarios_summary.csv) 

Please, keep in mind that the computational time to run the 4 scenarios is long.




More specifically, we commented:
- the last line of code of the `step` function of the `Vehicle` (Agent) class in the `components.py` file:
print(self). You can find the  step function in (components.py>Vehicle(Agent)>step()) function in the `Vehicle` class in the `components.py` file.
. 
- the print of the generation of trucks in the Source class in the `components.py` file. You can find the generation of trucks in the `generate` function in the `Source` class in the `components.py` file.
-  the print when removing class in the class Sink method Remove(). You can find the Remove function in the Sink class in the components.py file.
- An self-introduced print in the drive_to_next() method from the vehicle class in the components.py file.
- A self-introduce print of the chosen source and sink when computing the shortest path function in model.py file.

Lastly, find attached the results of the simulation in the [experiment](experiment) folder

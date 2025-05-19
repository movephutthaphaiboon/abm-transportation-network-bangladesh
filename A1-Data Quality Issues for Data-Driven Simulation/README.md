# README File

Created by:
|Group Number|16|
|:---:|:-------:|
|Rachel Delvin Sutiono|6284736|
|Celia Martínez Sillero| 6222102|
|Daniela Ríos Mora| 6275486|
|Thunchanok Phutthaphaiboon| 6141153|
|Yao Wang| 6157513|

## Introduction

In the folder (EPA133a-G16-A1),  can find place group 16's lab submission.

This README file is to help a first-time user understand what it is about and how they might be able to use it.


## Purpose and objective of this project

This project submission  evaluates data quality issues in Bangladesh s transport infrastructure dataset, which contains information on the locations of roads and bridges key elements for assessing bridge infrastructure criticality, vulnerability, and investment priorities. However, errors and missing details in the data can compromise simulation outcomes. To address this, we identify the main issues, propose strategies for resolution, prioritize the most critical problems, and implement selected solutions. The objective is to enhance data quality and ensure the dataset is ready for future simulation tasks.
## Structure

The following submission is provided with the following structure:
Structure inside this ZIP file: 

Folder EPA133a-G16-A1
  Subfolder "data"
    Subfolder "raw"
        BMMS_overview.xlsx
        _roads.tsv
    Subfolder "processed"
        -BMMS_overview.xlsx
        -BMMS_overview_cleaned_bridges_after_LPRE_removed.xlsx
        -BMMS_overview_cleaned_prelim.xlsx
        -BMMS_overview_removed_lrps.xlsx
        -_roads.tsv
        -_roads_cleaned.tsv
        -road_transposed.csv
  Subfolder "report"
    -EPA133a-G16-A1-Report.pdf
  Subfolder "notebook"
    -G16-A1-CleanRoads.ipynb
    -G16-A1-CleanBridges.ipynb
  README.txt (this file)

The most important files are located in data/processes. These are: BMMS_overview.xlsx and _roads.tsv. They are the final outputs from both notebooks.
  
 ## How to Use

First, run the program CleanRoads.ipynb. 
Inputs:  _roads.tsv from the folder in the path data/raw 
Outputs:  
1. new file called _roads.tsv and road_transposed.csv in the path data/processed 

Secondly, run the program CleanBridges.ipynb
Inputs: the BMMS_overview.xlsx from the folder in the path data/raw
The road_transposed.csv from the relative path data/processed folder, created by CleanRoads.py
Outputs:  This program outputs intermediate and final results in xlsx files in the path data/processed.

1. BMMS_overview_cleaned_prelim.xlsx
2. BMMS_overview_cleaned_bridges_after_LPRE_removed.xlsx
3. 'BMMS_overview_removed_lrps.xlsx' contains all bridges that have been removed by the algorithm
4. A new file called “BMMS_overview” in the data/processed path. This is the final output.

  Lastly, please make sure to attach the files _roads.tsv and BMMS_overview.xlsx into the folder with the relative path: \WBSIM_Lab1_2024\infrastructure. 
